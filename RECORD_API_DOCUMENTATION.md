# Record API Documentation

Base URL: `/api`

---

## Table of Contents
1. [CRUD Operations](#crud-operations)
   - [Create Record](#1-create-record)
   - [Get All Records](#2-get-all-records)
   - [Get Record by ID](#3-get-record-by-id)
   - [Update Record](#4-update-record)
   - [Delete Record](#5-delete-record)
2. [Query Operations](#query-operations)
   - [Get Records by Location (POST - Legacy)](#6-get-records-by-location-post---legacy)
   - [Get Records by Location (GET)](#7-get-records-by-location-get)
   - [Get Records by Location (POST - New)](#8-get-records-by-location-post---new)
3. [Debug Operations](#debug-operations)
   - [Debug All Records](#9-debug-all-records)
   - [Debug Records by Location](#10-debug-records-by-location)

---

## Data Models

### RecordCreate (Input)
```json
{
  "semester": "string",
  "date": "YYYY-MM-DD",
  "photo": "string (optional)",
  "description": "string (optional)",
  "location_id": "integer",
  "account_id": "integer"
}
```

### RecordUpdate (Input)
```json
{
  "semester": "string (optional)",
  "date": "YYYY-MM-DD (optional)",
  "photo": "string (optional)",
  "description": "string (optional)",
  "location_id": "integer (optional)",
  "account_id": "integer (optional)"
}
```

### RecordResponse (Output)
```json
{
  "record_id": "integer",
  "semester": "string",
  "date": "YYYY-MM-DD",
  "photo": "string or null",
  "description": "string or null",
  "location_id": "integer or null",
  "account_id": "integer or null"
}
```

---

## CRUD Operations

### 1. Create Record

**Endpoint:** `POST /create`

**Description:** Creates a new home visit record

**Request Body:**
```json
{
  "semester": "113-1",
  "date": "2024-03-15",
  "photo": "https://example.com/photo.jpg",
  "description": "家訪記錄描述",
  "location_id": 1,
  "account_id": 2
}
```

**Response:** `201 Created`
```json
{
  "status": "success",
  "message": "家訪記錄創建成功",
  "data": {
    "record_id": 1,
    "semester": "113-1",
    "date": "2024-03-15",
    "photo": "https://example.com/photo.jpg",
    "description": "家訪記錄描述",
    "location_id": 1,
    "account_id": 2
  }
}
```

**Error Response:** `500 Internal Server Error`
```json
{
  "detail": "創建記錄失敗: {error_message}"
}
```

---

### 2. Get All Records

**Endpoint:** `GET /records`

**Description:** Retrieves all home visit records with pagination

**Query Parameters:**
- `skip` (integer, optional, default=0, min=0): Number of records to skip
- `limit` (integer, optional, default=100, min=1, max=1000): Maximum number of records to return

**Example Request:**
```
GET /records?skip=0&limit=10
```

**Response:** `200 OK`
```json
{
  "status": "success",
  "data": [
    {
      "record_id": 1,
      "semester": "113-1",
      "date": "2024-03-15",
      "photo": "https://example.com/photo.jpg",
      "description": "家訪記錄描述",
      "location_id": 1,
      "account_id": 2
    },
    {
      "record_id": 2,
      "semester": "113-1",
      "date": "2024-03-20",
      "photo": null,
      "description": "另一筆家訪記錄",
      "location_id": 3,
      "account_id": 4
    }
  ],
  "total": 50,
  "skip": 0,
  "limit": 10,
  "returned": 2
}
```

**Empty Response:** `200 OK`
```json
{
  "status": "success",
  "data": [],
  "total": 0,
  "skip": 0,
  "limit": 10
}
```

**Error Response:** `500 Internal Server Error`
```json
{
  "detail": "獲取記錄失敗: {error_message}"
}
```

---

### 3. Get Record by ID

**Endpoint:** `GET /records/{record_id}`

**Description:** Retrieves a single home visit record by its ID

**Path Parameters:**
- `record_id` (integer, required): The record ID

**Example Request:**
```
GET /records/1
```

**Response:** `200 OK`
```json
{
  "status": "success",
  "data": {
    "record_id": 1,
    "semester": "113-1",
    "date": "2024-03-15",
    "photo": "https://example.com/photo.jpg",
    "description": "家訪記錄描述",
    "location_id": 1,
    "account_id": 2
  }
}
```

**Error Response:** `404 Not Found`
```json
{
  "detail": "找不到 ID 為 1 的家訪記錄"
}
```

**Error Response:** `500 Internal Server Error`
```json
{
  "detail": "獲取記錄失敗: {error_message}"
}
```

---

### 4. Update Record

**Endpoint:** `PUT /update/{record_id}`

**Description:** Updates an existing home visit record

**Path Parameters:**
- `record_id` (integer, required): The record ID to update

**Request Body:** (All fields are optional)
```json
{
  "semester": "113-2",
  "date": "2024-03-16",
  "photo": "https://example.com/new-photo.jpg",
  "description": "更新後的描述",
  "location_id": 2,
  "account_id": 3
}
```

**Response:** `200 OK`
```json
{
  "status": "success",
  "message": "家訪記錄更新成功",
  "data": {
    "record_id": 1,
    "semester": "113-2",
    "date": "2024-03-16",
    "photo": "https://example.com/new-photo.jpg",
    "description": "更新後的描述",
    "location_id": 2,
    "account_id": 3
  }
}
```

**Error Response:** `404 Not Found`
```json
{
  "detail": "找不到ID為 1 的家訪記錄"
}
```

**Error Response:** `500 Internal Server Error`
```json
{
  "detail": "更新記錄失敗: {error_message}"
}
```

---

### 5. Delete Record

**Endpoint:** `DELETE /delete/{record_id}`

**Description:** Deletes a home visit record

**Path Parameters:**
- `record_id` (integer, required): The record ID to delete

**Example Request:**
```
DELETE /delete/1
```

**Response:** `200 OK`
```json
{
  "status": "success",
  "message": "已成功刪除ID為 1 的家訪記錄"
}
```

**Error Response:** `404 Not Found`
```json
{
  "detail": "找不到ID為 1 的家訪記錄"
}
```

**Error Response:** `500 Internal Server Error`
```json
{
  "detail": "刪除記錄時發生錯誤: {error_message}"
}
```

---

## Query Operations

### 6. Get Records by Location (POST - Legacy)

**Endpoint:** `POST /records`

**Description:** Retrieves all home visit records for a specific location (legacy endpoint, maintains backward compatibility)

**Request Body:**
```json
{
  "locationid": 1
}
```

**Response:** `200 OK`
```json
{
  "status": "success",
  "data": [
    {
      "record_id": 1,
      "semester": "113-1",
      "date": "2024-03-15",
      "photo": "https://example.com/photo.jpg",
      "description": "家訪記錄描述",
      "location_id": 1,
      "account_id": 2,
      "account_info": {...},
      "location_info": {...},
      "students": [...],
      "villagers": [...]
    }
  ]
}
```

**Error Response:** `404 Not Found`
```json
{
  "detail": "沒有找到地點 ID=1 的家訪記錄"
}
```

**Error Response:** `500 Internal Server Error`
```json
{
  "detail": "伺服器內部錯誤: {error_message}"
}
```

---

### 7. Get Records by Location (GET)

**Endpoint:** `GET /records/location/{location_id}`

**Description:** Retrieves all home visit records for a specific location using GET method

**Path Parameters:**
- `location_id` (integer, required): The location ID

**Example Request:**
```
GET /records/location/1
```

**Response:** `200 OK`
```json
{
  "status": "success",
  "data": [
    {
      "record_id": 1,
      "semester": "113-1",
      "date": "2024-03-15",
      "photo": "https://example.com/photo.jpg",
      "description": "家訪記錄描述",
      "location_id": 1,
      "account_id": 2
    }
  ],
  "total": 1
}
```

**Empty Response:** `200 OK`
```json
{
  "status": "success",
  "data": [],
  "message": "地點 ID 1 沒有家訪記錄"
}
```

**Error Response:** `500 Internal Server Error`
```json
{
  "detail": "查詢記錄失敗: {error_message}"
}
```

---

### 8. Get Records by Location (POST - New)

**Endpoint:** `POST /records/by-location`

**Description:** Retrieves all home visit records for a specific location using new POST method

**Request Body:**
```json
{
  "location_id": 1
}
```

**Response:** `200 OK`
```json
{
  "status": "success",
  "data": [
    {
      "record_id": 1,
      "semester": "113-1",
      "date": "2024-03-15",
      "photo": "https://example.com/photo.jpg",
      "description": "家訪記錄描述",
      "location_id": 1,
      "account_id": 2
    }
  ],
  "total": 1
}
```

**Empty Response:** `200 OK`
```json
{
  "status": "success",
  "data": [],
  "message": "地點 ID 1 沒有家訪記錄"
}
```

**Error Response:** `500 Internal Server Error`
```json
{
  "detail": "查詢記錄失敗: {error_message}"
}
```

---

## Debug Operations

### 9. Debug All Records

**Endpoint:** `GET /records/debug/all`

**Description:** Debug endpoint to retrieve basic information about all records, including null field counts

**Example Request:**
```
GET /records/debug/all
```

**Response:** `200 OK`
```json
{
  "status": "success",
  "total_records": 10,
  "null_account_count": 2,
  "null_location_count": 1,
  "data": [
    {
      "record_id": 1,
      "location_id": 1,
      "account_id": 2,
      "semester": "113-1",
      "date": "2024-03-15",
      "has_null_account": false,
      "has_null_location": false
    },
    {
      "record_id": 2,
      "location_id": null,
      "account_id": null,
      "semester": "113-1",
      "date": "2024-03-20",
      "has_null_account": true,
      "has_null_location": true
    }
  ]
}
```

**Error Response:** `500 Internal Server Error`
```json
{
  "detail": "調試查詢錯誤: {error_message}"
}
```

---

### 10. Debug Records by Location

**Endpoint:** `GET /records/debug/location/{location_id}`

**Description:** Debug endpoint to inspect record query for a specific location, including conversion status

**Path Parameters:**
- `location_id` (integer, required): The location ID

**Example Request:**
```
GET /records/debug/location/1
```

**Response:** `200 OK`
```json
{
  "status": "debug",
  "location_id": 1,
  "raw_records_count": 2,
  "data": [
    {
      "raw_record": {
        "record_id": 1,
        "location": 1,
        "account": 2,
        "semester": "113-1",
        "date": "2024-03-15",
        "photo": "https://example.com/photo.jpg",
        "description": "家訪記錄描述"
      },
      "conversion_success": true,
      "conversion_error": null,
      "converted_response": {
        "record_id": 1,
        "semester": "113-1",
        "date": "2024-03-15",
        "photo": "https://example.com/photo.jpg",
        "description": "家訪記錄描述",
        "location_id": 1,
        "account_id": 2
      }
    }
  ]
}
```

**Error Response:** `500 Internal Server Error`
```json
{
  "detail": "調試查詢錯誤: {error_message}"
}
```

---

## HTTP Status Codes

- `200 OK` - Request successful
- `201 Created` - Resource created successfully
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error occurred

---

## Notes

1. **Date Format**: All dates use ISO 8601 format (YYYY-MM-DD)
2. **Pagination**: The GET /records endpoint supports pagination with skip and limit parameters
3. **Multiple Query Methods**: There are three different ways to query records by location for backward compatibility and flexibility
4. **Null Values**: Some fields (photo, description, location_id, account_id) may be null in responses
5. **Debug Endpoints**: Debug endpoints are for development/troubleshooting purposes only
