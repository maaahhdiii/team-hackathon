# File Server — Team C (Member 5 — solo)

## What you are building
A vulnerable file management service running on internal port 8003.
Users can upload and download files. When vulns are active, those operations can be abused.

## Internal port
8003

## Max HP
30

## Your vulnerabilities
| ID | Name | When ON | When OFF |
|----|------|---------|----------|
| path_traversal | Path Traversal | Serve raw file path — allows ../../etc/passwd | Strip to basename, serve only from /app/files/ |
| exec_upload | Exec Upload | Accept .php .sh .py .rb .pl .exe .bat files | Reject those extensions with 400 |

## Endpoints you must implement

### Vulnerable endpoints
- GET /download?file=filename.txt — returns file content as plain text
- POST /upload — multipart form field "file" — returns {"ok":true,"filename":"uploaded.txt"}
- GET /files/<filename> — serve any file from /app/files/
- GET /list — returns {"files":["sample.txt",...]}

### Path traversal logic
```python
# OFF (safe):
filename = os.path.basename(request.args.get("file",""))
safe_path = os.path.join(FILES_DIR, filename)
if not os.path.realpath(safe_path).startswith(os.path.realpath(FILES_DIR)):
    return jsonify({"error":"forbidden"}), 403

# ON (vulnerable):
safe_path = request.args.get("file")  # raw — no check
```

### Mandatory shared endpoints
- GET /health, POST /flags/activate, POST /flags/deactivate, POST /damage, POST /heal

## Seed files
Create /app/files/sample.txt with content: "This is a sample file. Hackathon platform v1.0"
Create /app/files/report.txt with content: "Q3 Report — Revenue: $1.2M — Confidential"

## Rules
- All vulnerabilities start INACTIVE
- FILES_DIR = "/app/files"
- BLOCKED_EXTENSIONS = [".php",".sh",".py",".rb",".pl",".exe",".bat"]
- Scope is small — 2 vulns, keep it focused

## Files to deliver
- app.py
- requirements.txt
- Dockerfile — FROM python:3.11-slim, expose 8003, CMD ["python3","app.py"]
- files/sample.txt
- files/report.txt

## Test your server
```bash
docker build -t file-server . && docker run -p 8003:8003 -e HACKATHON_SECRET=HACKATHON_SECRET_2025 file-server

# List files
curl http://localhost:8003/list

# Download safe file
curl "http://localhost:8003/download?file=sample.txt"

# Activate path_traversal
curl -X POST http://localhost:8003/flags/activate -H "Content-Type: application/json" -d '{"vuln":"path_traversal","secret":"HACKATHON_SECRET_2025"}'

# Try path traversal (should work when active)
curl "http://localhost:8003/download?file=../../etc/passwd"
```