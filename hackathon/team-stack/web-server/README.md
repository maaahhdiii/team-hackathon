# Web Server — Team A (Members 1 & 2)

## What you are building
A vulnerable Flask web application running on internal port 8001.
It must look like a real website with a login page, search, and comments.
Vulnerabilities are toggled ON/OFF by the orchestrator during the battle.

## Internal port
8001

## Max HP
40

## Your vulnerabilities
| ID | Name | When ON | When OFF |
|----|------|---------|----------|
| sqli | SQL Injection | Use raw string concat in SQL queries — injectable | Use parameterized queries |
| xss | XSS | Return raw unsanitized HTML from comment input | HTML-escape all output |
| auth_bypass | Auth Bypass | Accept any JWT without verifying signature | Verify JWT with secret key |

## Endpoints you must implement

### Vulnerable endpoints
- POST /login — body: {"username":"x","password":"y"} — returns {"token":"<jwt>"} or 401
- GET /search?q=term — returns {"results":[...]}
- POST /comment — body: {"text":"hello"} — returns {"ok":true,"comment":"<value>"}
- GET /comments — returns {"comments":[...]}
- GET /profile — requires Authorization: Bearer <token> header — returns {"user":"admin","role":"admin"}

### Mandatory shared endpoints (same on all 4 servers)
- GET /health → {"service":"web","status":"online","hp":40,"max_hp":40,"vulns_active":[],"timestamp":0}
- POST /flags/activate → body: {"vuln":"sqli","secret":"HACKATHON_SECRET_2025"} → {"ok":true,"vuln":"sqli","active":true}
- POST /flags/deactivate → same body → {"ok":true,"vuln":"sqli","active":false}
- POST /damage → body: {"amount":8,"secret":"HACKATHON_SECRET_2025"} → {"ok":true,"hp":32} — HP floor: 0, max 15 damage per 30s
- POST /heal → body: {"amount":5,"secret":"HACKATHON_SECRET_2025"} → {"ok":true,"hp":37} — HP ceiling: 40

## Rules
- All vulnerabilities must start as INACTIVE (False) on startup
- Never crash — always return JSON even on errors
- Read secret from env var: HACKATHON_SECRET
- Use sqlite3 for the DB. Seed on startup: admin/secret123 + 4 other users
- Use PyJWT for tokens. JWT secret when verifying: SUPER_SECRET_KEY_2025

## Files to deliver
- app.py — complete Flask application
- requirements.txt — all pip dependencies
- Dockerfile — FROM python:3.11-slim, expose port 8001, CMD ["python3","app.py"]

## Test your server
```bash
# Start
docker build -t web-server . && docker run -p 8001:8001 -e HACKATHON_SECRET=HACKATHON_SECRET_2025 web-server

# Test health
curl http://localhost:8001/health

# Test login (safe mode)
curl -X POST http://localhost:8001/login -H "Content-Type: application/json" -d '{"username":"admin","password":"secret123"}'

# Activate SQLi
curl -X POST http://localhost:8001/flags/activate -H "Content-Type: application/json" -d '{"vuln":"sqli","secret":"HACKATHON_SECRET_2025"}'

# Test SQLi (should work when active)
curl -X POST http://localhost:8001/login -H "Content-Type: application/json" -d '{"username":"'"'"' OR '"'"'1'"'"'='"'"'1'"'"' --","password":"x"}'
```