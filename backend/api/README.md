# Scout Badge Inventory API Documentation

This directory contains all API endpoint routers for the Scout Badge Inventory application.

## Overview

The API is built using FastAPI and provides endpoints for:
- Image upload and management
- Badge recognition and processing
- Inventory management
- Report generation

## API Endpoints

### Upload API

#### POST /api/upload

Upload one or more badge images for processing.

**Request:**
- Content-Type: `multipart/form-data`
- Body: Multiple file fields named `files`

**File Requirements:**
- Accepted formats: JPG, JPEG, PNG, HEIC
- Maximum file size: 10MB per file
- Multiple files allowed

**Example Request (cURL):**
```bash
curl -X POST "http://localhost:8000/api/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "files=@image1.jpg" \
  -F "files=@image2.jpg" \
  -F "files=@image3.png"
```

**Example Request (Python):**
```python
import requests

url = "http://localhost:8000/api/upload"
files = [
    ('files', open('image1.jpg', 'rb')),
    ('files', open('image2.jpg', 'rb')),
]

response = requests.post(url, files=files)
print(response.json())
```

**Example Request (JavaScript):**
```javascript
const formData = new FormData();
formData.append('files', file1);
formData.append('files', file2);

const response = await fetch('http://localhost:8000/api/upload', {
  method: 'POST',
  body: formData,
});

const data = await response.json();
console.log(data);
```

**Success Response (201 Created):**
```json
{
  "scan_id": 1,
  "status": "pending",
  "total_images": 3,
  "images": [
    {
      "original_filename": "badges_photo1.jpg",
      "saved_filename": "a1b2c3d4-e5f6-7890-abcd-ef1234567890.jpg",
      "file_size_bytes": 2458320,
      "file_path": "data/uploads/a1b2c3d4-e5f6-7890-abcd-ef1234567890.jpg"
    },
    {
      "original_filename": "badges_photo2.jpg",
      "saved_filename": "b2c3d4e5-f6a7-8901-bcde-f12345678901.jpg",
      "file_size_bytes": 3125478,
      "file_path": "data/uploads/b2c3d4e5-f6a7-8901-bcde-f12345678901.jpg"
    },
    {
      "original_filename": "inventory_scan.png",
      "saved_filename": "c3d4e5f6-a7b8-9012-cdef-123456789012.png",
      "file_size_bytes": 1987654,
      "file_path": "data/uploads/c3d4e5f6-a7b8-9012-cdef-123456789012.png"
    }
  ],
  "created_at": "2025-11-02T23:45:30.123456",
  "message": "Successfully uploaded 3 image(s). Scan ID: 1"
}
```

**Error Responses:**

**400 Bad Request - No files provided:**
```json
{
  "detail": "No files provided. Please upload at least one image."
}
```

**400 Bad Request - Invalid file type:**
```json
{
  "detail": "Invalid file type: document.pdf. Allowed types: .jpg, .jpeg, .png, .heic"
}
```

**413 Payload Too Large - File too large:**
```json
{
  "detail": "File too large: huge_image.jpg. Maximum size: 10.0MB"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "An unexpected error occurred during upload: [error message]"
}
```

---

#### GET /api/upload/status/{scan_id}

Get the status of a scan by its ID.

**Parameters:**
- `scan_id` (path parameter): The ID of the scan to query

**Example Request:**
```bash
curl -X GET "http://localhost:8000/api/upload/status/1" \
  -H "accept: application/json"
```

**Success Response (200 OK):**
```json
{
  "scan_id": 1,
  "status": "pending",
  "total_images": 3,
  "processed_images": 0,
  "progress_percentage": 0.0,
  "created_at": "2025-11-02T23:45:30.123456"
}
```

**Error Response (404 Not Found):**
```json
{
  "detail": "Scan with ID 999 not found"
}
```

---

## Response Models

### UploadResponse

```typescript
{
  scan_id: number;           // Unique identifier for this scan
  status: string;            // "pending", "processing", "completed", or "failed"
  total_images: number;      // Total number of images uploaded
  images: ImageUploadInfo[]; // Array of uploaded image details
  created_at: string;        // ISO timestamp of scan creation
  message: string;           // Success message
}
```

### ImageUploadInfo

```typescript
{
  original_filename: string;  // Original filename
  saved_filename: string;     // UUID-based filename on disk
  file_size_bytes: number;    // File size in bytes
  file_path: string;          // Relative path to saved file
}
```

---

## Error Handling

All endpoints follow standard HTTP status codes:

- **200 OK**: Request successful (GET requests)
- **201 Created**: Resource created successfully (POST requests)
- **400 Bad Request**: Invalid input (wrong file type, missing files, etc.)
- **404 Not Found**: Resource not found
- **413 Payload Too Large**: File exceeds size limit
- **500 Internal Server Error**: Server-side error

Error responses include a `detail` field with a descriptive message.

---

## Security Considerations

### Filename Sanitization

All uploaded filenames are sanitized to prevent security issues:
- Path traversal characters are removed
- Only alphanumeric characters, dots, hyphens, and underscores are allowed
- Files are renamed with UUID-based filenames

### File Type Validation

Only image files are accepted:
- `.jpg`, `.jpeg` - JPEG images
- `.png` - PNG images
- `.heic` - HEIC images (iPhone format)

File type validation is performed on the file extension. For production use, consider adding MIME type validation.

### File Size Limits

Maximum file size is 10MB per file. This prevents:
- Denial of service attacks
- Excessive storage usage
- Long upload times

### Database Transactions

All database operations use transactions with automatic rollback on errors. If any operation fails:
- Database changes are rolled back
- Uploaded files are deleted
- Appropriate error is returned to client

---

## Testing

### Interactive API Documentation

FastAPI provides interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

You can test all endpoints directly from the browser using these interfaces.

### Manual Testing with cURL

**Upload single image:**
```bash
curl -X POST "http://localhost:8000/api/upload" \
  -F "files=@/path/to/image.jpg"
```

**Upload multiple images:**
```bash
curl -X POST "http://localhost:8000/api/upload" \
  -F "files=@image1.jpg" \
  -F "files=@image2.jpg" \
  -F "files=@image3.png"
```

**Check scan status:**
```bash
curl -X GET "http://localhost:8000/api/upload/status/1"
```

### Testing Error Cases

**Test invalid file type:**
```bash
curl -X POST "http://localhost:8000/api/upload" \
  -F "files=@document.pdf"
# Expected: 400 Bad Request
```

**Test no files:**
```bash
curl -X POST "http://localhost:8000/api/upload"
# Expected: 400 Bad Request
```

**Test non-existent scan:**
```bash
curl -X GET "http://localhost:8000/api/upload/status/999999"
# Expected: 404 Not Found
```

---

## Database Schema

### Scans Table

Tracks upload sessions and processing status.

```sql
CREATE TABLE scans (
    id INTEGER PRIMARY KEY,
    created_at DATETIME NOT NULL,
    status TEXT NOT NULL,  -- 'pending', 'processing', 'completed', 'failed'
    total_images INTEGER NOT NULL,
    processed_images INTEGER NOT NULL,
    notes TEXT
);
```

### Scan Images Table

Tracks individual images within a scan.

```sql
CREATE TABLE scan_images (
    id INTEGER PRIMARY KEY,
    scan_id INTEGER NOT NULL,
    image_path TEXT NOT NULL,
    uploaded_at DATETIME NOT NULL,
    processed_at DATETIME,
    status TEXT NOT NULL,  -- 'pending', 'processing', 'completed', 'failed'
    FOREIGN KEY (scan_id) REFERENCES scans(id)
);
```

---

## Configuration

Upload settings are configured in `backend/config.py`:

```python
class UploadConfig:
    UPLOAD_DIR = Path("data/uploads")       # Upload directory
    MAX_FILE_SIZE = 10485760                # 10MB in bytes
    ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".heic"}
```

To modify settings, either:
1. Edit `config.py` directly
2. Set environment variables:
   ```bash
   export UPLOAD_DIR="custom/upload/path"
   export MAX_FILE_SIZE="20971520"  # 20MB
   ```

---

## Next Steps

After uploading images, use the scan_id to:
1. Process images with AI: `POST /api/process/{scan_id}` (Coming in ACTION-206)
2. Review detected badges: `GET /api/scans/{scan_id}/results` (Coming soon)
3. Update inventory: `POST /api/inventory/adjust` (Coming in ACTION-207)

---

## Support

For issues or questions:
1. Check the API documentation at `/docs`
2. Review error messages in responses
3. Check server logs for detailed error information
4. Refer to the main project README.md

---

## Changelog

### Version 1.0.0 (2025-11-02)
- Initial implementation of upload API
- Support for JPG, JPEG, PNG, HEIC formats
- File validation and sanitization
- Database integration with Scan and ScanImage models
- Comprehensive error handling
- Status endpoint for tracking upload progress
