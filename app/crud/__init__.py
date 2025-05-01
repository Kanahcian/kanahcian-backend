# Import all CRUD modules
from app.crud.Location import get_locations, add_location, update_location, delete_location
from app.crud.Record import get_records, get_record_by_location, get_record_by_location_with_details, get_students_by_record, get_villagers_by_record
from app.crud.Villager import get_villager_by_id, get_villagers, get_villagers_by_location, create_villager, update_villager, delete_villager, create_relationship, delete_relationship, get_villager_relationships