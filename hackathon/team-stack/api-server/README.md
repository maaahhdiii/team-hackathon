# API Server — Team B (Members 3 & 4)

## What you are building
A vulnerable REST API running on internal port 8002.
Simulates a backend service with users, admin commands, and unprotected endpoints.

## Internal port
8002

## Max HP
30

## Your vulnerabilities
| ID | Name | When ON | When OFF |
|----|------|---------|----------|
| insecure_ep | Insecure Endpoints | /users and /admin need no authentication | Require auth headers |
| cmd_inject | Command Injection | Execute raw OS command from request body | Whitelist safe commands only |
| idor | IDOR | Return any user's data without ownership check | Verify requesting user owns the resource |

## Endpoints you must implement

### Vulnerable endpoints
- GET /users — returns {"users":[...]} — protected by insecure_ep flag
- GET /users/<int:user_id> — returns user dict — protected by idor flag
- POST /run — body: {"cmd":"whoami"} — returns {"output":"..."} — protected by cmd_inject flag
- GET /admin — returns {"message":"welcome admin"} — protected by insecure_ep flag

### Auth when insecure_ep is OFF
- GET /users and GET /admin require header: Authorization: Bearer admin-token-2025
- GET /admin also accepts: X-Admin-Key: admin-secret-2025
- GET /users/<id> requires header: X-User-Id matching the requested ID

### Mandatory shared endpoints
- GET /health, POST /flags/activate, POST /flags/deactivate, POST /damage, POST /heal
- (same contract as web-server — see web-server README for full spec)

## Seed data (in-memory, no DB needed)
```python
USERS = [
    {"id":1,"name":"alice","email":"alice@hack.com","role":"user"},
    {"id":2,"name":"bob","email":"bob@hack.com","role":"admin"},
    {"id":3,"name":"charlie","email":"charlie@hack.com","role":"user"},
    {"id":4,"name":"diana","email":"diana@hack.com","role":"user"},
    {"id":5,"name":"eve","email":"eve@hack.com","role":"admin"},
]
SAFE_COMMANDS = ["ping","whoami","date","uptime"]
```

## Rules
- All vulnerabilities start INACTIVE
- cmd_inject OFF: if cmd.split()[0] not in SAFE_COMMANDS → return 400
- cmd_inject ON: os.popen(cmd).read() or subprocess.getoutput(cmd)
- Never crash — always return JSON

## Files to deliver
- app.py — complete Flask application
- requirements.txt
- Dockerfile — FROM python:3.11-slim, expose 8002, CMD ["python3","app.py"]

## Test your server
```bash
docker build -t api-server . && docker run -p 8002:8002 -e HACKATHON_SECRET=HACKATHON_SECRET_2025 api-server

# Health check
curl http://localhost:8002/health

# Test without auth (should fail with 401 when insecure_ep is OFF)
curl http://localhost:8002/users

# Activate insecure_ep
curl -X POST http://localhost:8002/flags/activate -H "Content-Type: application/json" -d '{"vuln":"insecure_ep","secret":"HACKATHON_SECRET_2025"}'

# Test without auth (should work now)
curl http://localhost:8002/users
```