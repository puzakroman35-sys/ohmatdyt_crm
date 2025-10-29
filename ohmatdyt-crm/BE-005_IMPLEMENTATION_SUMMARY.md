# BE-005 Implementation Summary

## Overview
Implemented file attachment functionality for cases with comprehensive validation, storage management, and RBAC controls.

## Implementation Date
October 28, 2025

## Components Implemented

### 1. Database Model (`app/models.py`)
- **Attachment Model**:
  - `id` (UUID, primary key)
  - `case_id` (UUID, foreign key to cases)
  - `file_path` (String, relative path from MEDIA_ROOT)
  - `original_name` (String, original filename)
  - `size_bytes` (Integer, file size)
  - `mime_type` (String, MIME type)
  - `uploaded_by_id` (UUID, foreign key to users)
  - `created_at` (DateTime)
  - Relationships to Case and User models
  - CASCADE delete when case is deleted

### 2. Validation Utilities (`app/utils.py`)

#### File Type Validation
- **Allowed Document Types**:
  - PDF (`.pdf`)
  - Microsoft Word (`.doc`, `.docx`)
  - Microsoft Excel (`.xls`, `.xlsx`)

- **Allowed Image Types**:
  - JPEG (`.jpg`, `.jpeg`)
  - PNG (`.png`)

#### File Size Validation
- **Maximum Size**: 10MB (10,485,760 bytes)
- Validates both file size and checks for empty files

#### Security Features
- **Filename Sanitization**:
  - Removes path separators
  - Replaces unsafe characters
  - Limits filename length to 255 characters
  - Adds UUID prefix to prevent name collisions

- **Path Security**:
  - Storage hierarchy: `/media/cases/{public_id}/{uuid}_{filename}`
  - Prevents directory traversal attacks
  - Uses MEDIA_ROOT for all file operations

### 3. Pydantic Schemas (`app/schemas.py`)
- **AttachmentBase**: Base schema with file metadata
- **AttachmentResponse**: Full response with IDs and timestamps
- **AttachmentListResponse**: Paginated list of attachments

### 4. CRUD Operations (`app/crud.py`)
- `create_attachment()`: Create attachment database record
- `get_attachment()`: Get attachment by ID
- `get_case_attachments()`: List all attachments for a case
- `delete_attachment()`: Delete attachment record (not file)

### 5. API Endpoints (`app/routers/attachments.py`)

#### POST `/api/attachments/cases/{case_id}/upload`
- Upload file attachment to a case
- Validates file type and size
- Stores file in hierarchical structure
- Returns attachment metadata
- **RBAC**:
  - OPERATOR: Can upload to own cases
  - EXECUTOR/ADMIN: Can upload to any case

#### GET `/api/attachments/cases/{case_id}`
- List all attachments for a specific case
- Supports pagination (skip/limit)
- Returns attachment metadata list
- **RBAC**:
  - OPERATOR: Can view attachments for own cases
  - EXECUTOR/ADMIN: Can view all attachments

#### GET `/api/attachments/{attachment_id}/download`
- Download attachment file
- Returns file with original name
- Serves correct MIME type
- **RBAC**:
  - OPERATOR: Can download from own cases
  - EXECUTOR/ADMIN: Can download all attachments

#### DELETE `/api/attachments/{attachment_id}`
- Delete attachment (both file and database record)
- Removes physical file from disk
- Removes database record
- **RBAC**:
  - OPERATOR: Can delete from own cases
  - ADMIN: Can delete any attachment
  - EXECUTOR: **Cannot** delete attachments

### 6. Database Migration
- **Migration ID**: `e9f3a5b2c8d1`
- Creates `attachments` table with proper indexes
- Foreign keys with appropriate CASCADE/RESTRICT behaviors
- Indexes on: `id`, `case_id`, `uploaded_by_id`, `created_at`

### 7. File Storage
- **Storage Location**: `MEDIA_ROOT/cases/{public_id}/{uuid}_{filename}`
- Automatic directory creation
- UUID prefix prevents filename collisions
- Hierarchical organization by case public_id

## Validation Rules

### File Type Validation
```python
ALLOWED_MIME_TYPES = {
    'application/pdf': ['.pdf'],
    'application/msword': ['.doc'],
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    'application/vnd.ms-excel': ['.xls'],
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
    'image/jpeg': ['.jpg', '.jpeg'],
    'image/png': ['.png'],
}
```

### Size Limits
- **Maximum**: 10MB (10,485,760 bytes)
- **Minimum**: > 0 bytes (no empty files)

### Error Responses
- **400 Bad Request**:
  - Invalid file type
  - File too large
  - Empty file
  - Invalid MIME type
  - Extension/MIME type mismatch
  
- **403 Forbidden**:
  - Insufficient permissions for case
  - Executor trying to delete attachment
  
- **404 Not Found**:
  - Case not found
  - Attachment not found
  - File not found on disk

## RBAC Matrix

| Operation | OPERATOR | EXECUTOR | ADMIN |
|-----------|----------|----------|-------|
| Upload to own case | ✅ | N/A | ✅ |
| Upload to any case | ❌ | ✅ | ✅ |
| List own case attachments | ✅ | N/A | ✅ |
| List any case attachments | ❌ | ✅ | ✅ |
| Download own case attachment | ✅ | N/A | ✅ |
| Download any attachment | ❌ | ✅ | ✅ |
| Delete own case attachment | ✅ | ❌ | ✅ |
| Delete any attachment | ❌ | ❌ | ✅ |

## Testing (`test_be005.py`)

### Test Coverage
1. ✅ Upload valid file types (PDF, DOC, DOCX, XLS, XLSX, JPG, PNG)
2. ✅ Reject invalid file type (.exe)
3. ✅ Reject oversized file (>10MB)
4. ✅ List case attachments
5. ✅ Download attachment
6. ✅ RBAC: Operator cannot access other's attachments
7. ✅ Delete attachment (file + DB record)

### Running Tests
```bash
# Set API URL (if not default)
export API_BASE_URL=http://localhost:8001

# Run tests
python test_be005.py
```

## Dependencies
All required dependencies already present in `requirements.txt`:
- `fastapi` - Web framework
- `python-multipart` - File upload support
- `sqlalchemy` - ORM and database
- `pydantic` - Data validation

## Configuration
Required environment variables (in `.env`):
```env
MEDIA_ROOT=/var/app/media
```

## File Organization

```
ohmatdyt-crm/
├── api/
│   ├── app/
│   │   ├── models.py           # Added Attachment model
│   │   ├── schemas.py          # Added attachment schemas
│   │   ├── crud.py             # Added attachment CRUD
│   │   ├── utils.py            # Added file validation
│   │   ├── main.py             # Registered attachments router
│   │   └── routers/
│   │       └── attachments.py  # New: Attachment endpoints
│   ├── alembic/
│   │   └── versions/
│   │       └── e9f3a5b2c8d1_create_attachments_table.py
│   └── test_be005.py           # New: Test suite
└── media/                      # File storage (Docker volume)
    └── cases/
        └── {public_id}/
            └── {uuid}_{filename}
```

## Security Considerations

### Implemented Protections
1. **File Type Validation**: Whitelist approach, only specific MIME types allowed
2. **Size Limits**: Prevents DoS via large file uploads
3. **Filename Sanitization**: Prevents path traversal and injection attacks
4. **UUID Prefixes**: Prevents filename collision and enumeration
5. **RBAC Controls**: Strict permission checks on all operations
6. **CASCADE Delete**: Attachments automatically deleted when case is deleted
7. **Separate Storage**: Files stored outside application directory

### Potential Enhancements (Future)
- Virus scanning integration
- File content validation (magic bytes)
- CDN integration for large files
- Thumbnail generation for images
- Compression for large documents
- Audit logging for downloads
- Rate limiting on uploads

## Migration Steps

### 1. Apply Database Migration
```bash
cd api
alembic upgrade head
```

### 2. Ensure Media Directory Exists
Docker Compose automatically creates the volume, but for manual setup:
```bash
mkdir -p /var/app/media/cases
chmod 755 /var/app/media
```

### 3. Restart Services
```bash
docker compose restart api worker beat
```

## API Examples

### Upload Attachment
```bash
curl -X POST \
  http://localhost:8001/api/attachments/cases/{case_id}/upload \
  -H "Authorization: Bearer {token}" \
  -F "file=@document.pdf"
```

### List Attachments
```bash
curl -X GET \
  http://localhost:8001/api/attachments/cases/{case_id} \
  -H "Authorization: Bearer {token}"
```

### Download Attachment
```bash
curl -X GET \
  http://localhost:8001/api/attachments/{attachment_id}/download \
  -H "Authorization: Bearer {token}" \
  -o downloaded_file.pdf
```

### Delete Attachment
```bash
curl -X DELETE \
  http://localhost:8001/api/attachments/{attachment_id} \
  -H "Authorization: Bearer {token}"
```

## Completion Status
✅ **COMPLETED** - All requirements from BE-005 implemented and tested

## DoD Verification
- ✅ Files with disallowed type/size rejected (400)
- ✅ Valid files stored and accessible for download
- ✅ RBAC enforced on all operations
- ✅ File hierarchy: `/cases/{public_id}/...`
- ✅ Comprehensive test suite created
- ✅ Database migration created and tested
