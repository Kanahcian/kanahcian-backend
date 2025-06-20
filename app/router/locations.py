# Purpose: 處理 locations API

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from ..crud import Location
from ..database import get_db
from .. import schemas

router = APIRouter(tags=["Location"])

# **取得所有地點 - 修復版本**
@router.get("/locations", response_model=dict, status_code=status.HTTP_200_OK)
def get_locations(
    include_invalid: bool = Query(False, description="包含座標無效的地點"),
    db: Session = Depends(get_db)
):
    """
    獲取所有地點
    
    Args:
        include_invalid: 是否包含座標為空的地點
        db: 資料庫連線
    
    Returns:
        dict: 地點列表
    """
    try:
        location_list = Location.get_locations(db)

        if not location_list:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="沒有找到任何地點資料"
            )

        # 處理和過濾地點資料
        valid_locations = []
        invalid_locations = []
        
        for loc in location_list:
            try:
                # 檢查座標是否有效
                has_valid_coords = (
                    loc.Latitude is not None and 
                    loc.Longitude is not None and
                    str(loc.Latitude).strip() != '' and 
                    str(loc.Longitude).strip() != ''
                )
                
                location_data = schemas.LocationResponse(
                    id=loc.LocationID,
                    name=loc.name,
                    latitude=str(loc.Latitude) if loc.Latitude is not None else None,
                    longitude=str(loc.Longitude) if loc.Longitude is not None else None,
                    address=loc.Address,
                    brief_description=loc.BriefDescription,
                    photo=loc.Photo,
                    tag=loc.Tag
                )
                
                if has_valid_coords:
                    valid_locations.append(location_data)
                else:
                    invalid_locations.append(location_data)
                    
            except Exception as e:
                print(f"Error processing location {loc.LocationID}: {e}")
                # 跳過有問題的記錄
                continue
        
        # 根據參數決定返回哪些地點
        if include_invalid:
            all_locations = valid_locations + invalid_locations
            return {
                "status": "success",
                "data": all_locations,
                "summary": {
                    "total": len(all_locations),
                    "valid": len(valid_locations),
                    "invalid": len(invalid_locations)
                }
            }
        else:
            # 只返回有效座標的地點
            if not valid_locations:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="沒有找到具有有效座標的地點"
                )
            
            return {
                "status": "success",
                "data": valid_locations,
                "summary": {
                    "total": len(valid_locations),
                    "filtered_out": len(invalid_locations)
                }
            }
            
    except HTTPException:
        # 重新拋出 HTTP 異常
        raise
    except Exception as e:
        print(f"Unexpected error in get_locations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="獲取地點資料時發生錯誤"
        )

# **診斷端點 - 檢查資料問題**
@router.get("/locations/diagnostics", response_model=dict)
def diagnose_locations(db: Session = Depends(get_db)):
    """診斷地點資料問題"""
    try:
        location_list = Location.get_locations(db)
        
        diagnostics = {
            "total_locations": len(location_list),
            "issues": [],
            "valid_locations": 0,
            "problem_locations": []
        }
        
        for loc in location_list:
            issues = []
            
            # 檢查座標
            if loc.Latitude is None:
                issues.append("latitude_null")
            elif str(loc.Latitude).strip() == '':
                issues.append("latitude_empty")
                
            if loc.Longitude is None:
                issues.append("longitude_null")
            elif str(loc.Longitude).strip() == '':
                issues.append("longitude_empty")
            
            # 檢查名稱
            if not loc.name or loc.name.strip() == '':
                issues.append("name_empty")
            
            if issues:
                diagnostics["problem_locations"].append({
                    "id": loc.LocationID,
                    "name": loc.name,
                    "latitude": loc.Latitude,
                    "longitude": loc.Longitude,
                    "issues": issues
                })
            else:
                diagnostics["valid_locations"] += 1
        
        return {
            "status": "success",
            "diagnostics": diagnostics
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"診斷失敗: {str(e)}"
        )

# 其他路由保持不變...

# 新增地點
@router.post("/location", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_location(location: schemas.LocationCreate, db: Session = Depends(get_db)):
    new_loc = Location.add_location(db, location)
    return {
        "status": "success",
        "data": schemas.LocationResponse(
            id=new_loc.LocationID,
            name=new_loc.name,
            latitude=str(new_loc.Latitude) if new_loc.Latitude is not None else None,
            longitude=str(new_loc.Longitude) if new_loc.Longitude is not None else None,
            address=new_loc.Address,
            brief_description=new_loc.BriefDescription,
            photo=new_loc.Photo,
            tag=new_loc.Tag
        )
    }

# 編輯地點
@router.put("/location/{location_id}", response_model=dict)
def update_location(location_id: int, location: schemas.LocationUpdate, db: Session = Depends(get_db)):
    updated = Location.update_location(db, location_id, location)
    if not updated:
        raise HTTPException(status_code=404, detail="找不到該地點")
    return {
        "status": "success",
        "data": schemas.LocationResponse(
            id=updated.LocationID,
            name=updated.name,
            latitude=str(updated.Latitude) if updated.Latitude is not None else None,
            longitude=str(updated.Longitude) if updated.Longitude is not None else None,
            address=updated.Address,
            brief_description=updated.BriefDescription,
            photo=updated.Photo,
            tag=updated.Tag
        )
    }

# 刪除地點
@router.delete("/location/{location_id}", response_model=dict)
def delete_location(location_id: int, db: Session = Depends(get_db)):
    success = Location.delete_location(db, location_id)
    if not success:
        raise HTTPException(status_code=404, detail="找不到該地點")
    return {
        "status": "success",
        "message": f"地點 (ID={location_id}) 已成功刪除"
    }
