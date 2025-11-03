# Quick Testing Guide for ACTION-203

## 1. Start the Server

```bash
cd backend
uvicorn main:app --reload
```

Server starts at: http://localhost:8000

## 2. Open Interactive Documentation

Visit: http://localhost:8000/docs

## 3. Test the Upload Endpoint

### Option A: Using Swagger UI (Easiest)
1. Go to http://localhost:8000/docs
2. Click on "POST /api/upload"
3. Click "Try it out"
4. Click "Choose Files" and select image files
5. Click "Execute"
6. See the response with scan_id

### Option B: Using cURL
```bash
# Create test images first
python test_upload_api.py

# Upload images
curl -X POST "http://localhost:8000/api/upload" \
  -F "files=@test_images/test_badge1.jpg" \
  -F "files=@test_images/test_badge2.jpg" \
  -F "files=@test_images/test_badge3.png"
```

### Option C: Using Python
```python
import requests

url = "http://localhost:8000/api/upload"
files = [
    ('files', open('test_images/test_badge1.jpg', 'rb')),
    ('files', open('test_images/test_badge2.jpg', 'rb')),
]

response = requests.post(url, files=files)
print(response.json())
```

## 4. Verify Upload

Check scan status (replace 1 with your scan_id):
```bash
curl http://localhost:8000/api/upload/status/1
```

Check uploaded files:
```bash
ls -lh data/uploads/
```

## 5. Test Error Cases

**Invalid file type:**
```bash
echo "test" > test.txt
curl -X POST "http://localhost:8000/api/upload" -F "files=@test.txt"
# Expected: 400 Bad Request
```

**No files:**
```bash
curl -X POST "http://localhost:8000/api/upload"
# Expected: 400 Bad Request
```

## Expected Response

```json
{
  "scan_id": 1,
  "status": "pending",
  "total_images": 3,
  "images": [
    {
      "original_filename": "test_badge1.jpg",
      "saved_filename": "550e8400-e29b-41d4-a716-446655440000.jpg",
      "file_size_bytes": 123456,
      "file_path": "data/uploads/550e8400-e29b-41d4-a716-446655440000.jpg"
    }
  ],
  "created_at": "2025-11-02T23:45:30.123456",
  "message": "Successfully uploaded 3 image(s). Scan ID: 1"
}
```

## Troubleshooting

**Server won't start:**
- Check if another process is using port 8000
- Verify virtual environment is activated
- Check requirements are installed: `pip install -r requirements.txt`

**Database error:**
- Ensure database is initialized: Check backend/README.md
- Verify database path in config.py

**Upload fails:**
- Check data/uploads/ directory exists and is writable
- Verify file is < 10MB
- Verify file extension is .jpg, .jpeg, .png, or .heic
