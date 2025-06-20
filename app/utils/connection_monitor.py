# app/utils/connection_monitor.py - 連接監控和自動修復

import logging
import threading
import time
from sqlalchemy import text
from app.database import engine, SessionLocal

logger = logging.getLogger(__name__)

class ConnectionMonitor:
    def __init__(self, check_interval=60, max_connections=20):
        self.check_interval = check_interval
        self.max_connections = max_connections
        self.stop_event = threading.Event()
        self.monitor_thread = None
        
    def start_monitoring(self):
        """開始監控連接池"""
        if self.monitor_thread is None or not self.monitor_thread.is_alive():
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            logger.info("Connection monitor started")
    
    def stop_monitoring(self):
        """停止監控"""
        self.stop_event.set()
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)
        logger.info("Connection monitor stopped")
    
    def _monitor_loop(self):
        """監控循環"""
        while not self.stop_event.is_set():
            try:
                self._check_connections()
                time.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Connection monitor error: {e}")
                time.sleep(30)  # 錯誤時等待30秒後重試
    
    def _check_connections(self):
        """檢查連接狀態"""
        try:
            # 獲取連接池統計
            pool = engine.pool
            checked_out = pool.checkedout()
            pool_size = pool.size()
            overflow = pool.overflow()
            
            logger.info(f"Connection pool status - Size: {pool_size}, Checked out: {checked_out}, Overflow: {overflow}")
            
            # 如果連接數過高，執行清理
            if checked_out > self.max_connections:
                logger.warning(f"High connection count detected: {checked_out}/{self.max_connections}")
                self._force_cleanup()
            
            # 測試連接有效性
            self._test_connection()
            
        except Exception as e:
            logger.error(f"Error checking connections: {e}")
    
    def _force_cleanup(self):
        """強制清理連接池"""
        try:
            logger.info("Forcing connection pool cleanup...")
            
            # 回收所有閒置連接
            engine.pool.dispose()
            
            # 等待一段時間讓連接重新建立
            time.sleep(5)
            
            logger.info("Connection pool cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during connection cleanup: {e}")
    
    def _test_connection(self):
        """測試資料庫連接"""
        db = None
        try:
            db = SessionLocal()
            result = db.execute(text("SELECT 1")).scalar()
            if result != 1:
                logger.warning("Database connection test failed - unexpected result")
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
        finally:
            if db:
                try:
                    db.close()
                except Exception as close_error:
                    logger.error(f"Error closing test connection: {close_error}")

# 全局監控實例
connection_monitor = ConnectionMonitor(check_interval=60, max_connections=15)

