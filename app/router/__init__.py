# app/crud/__init__.py - 修復版本

# Import Location CRUD
from app.crud.Location import get_locations, add_location, update_location, delete_location

# Import Record CRUD - 確保所有函數都存在
from app.crud.Record import (
    # 新版函數
    get_all_records, 
    get_record_by_id, 
    get_records_by_location, 
    get_records_by_account, 
    get_records_by_semester,
    create_record, 
    update_record, 
    delete_record,
    get_records_count,
    get_records_count_by_location,
    
    # 舊版兼容函數
    get_records,
    get_record_by_location,
    get_record_by_location_with_details,
    get_students_by_record,
    get_villagers_by_record
)

# Import Villager CRUD
from app.crud.Villager import (
    get_villager_by_id, 
    get_villagers, 
    get_villagers_by_location, 
    create_villager, 
    update_villager, 
    delete_villager, 
    create_relationship, 
    delete_relationship, 
    get_villager_relationships
)