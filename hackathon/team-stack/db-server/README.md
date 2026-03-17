# DB Server — Team D (Member 6 — solo)

## What you are building
A vulnerable database-backed service running on internal port 8004.
Exposes query and user management endpoints. Attackers can extract data or escalate privileges.

## Internal port
8004

## Max HP
30

## Your vulnerabilities
| ID | Name | When ON | When OFF |
|----|------|---------|----------|
| sqli | SQL Injection | Raw string concat in query — injectable | Parameterized query |
| priv_esc | Privilege Escalation | Promote user without checking requester role | Verify requester is admin before promoting |

## Endpoints you must implement

### Vulnerable endpoints
- POST /query — body: {"search":"alice"} — returns {"results":[...]}
- GET /user/<int:user_id> — returns {"id":1,"name":"alice","role":"user"}
- POST /user/<int:user_id>/promote — body: {"requester_id":2} — returns {"ok":true,"user_id":1,"new_role":"admin"}
- GET /tables — returns {"tables":["users"]} or all tables if priv_esc ON

### SQLi logic
```python
# OFF (safe):
cursor.execute("SELECT id,name,role FROM users WHERE name LIKE ?", (f"%{search}%",))

# ON (vulnerable):
cursor.execute(f"SELECT id,name,role FROM users WHERE name LIKE '%{search}%'")
```

### Privilege escalation logic
```python
# OFF: fetch requester from DB, check role == "admin" before promoting
# ON: promote without any role check
```

### Mandatory shared endpoints
- GET /health, POST /flags/activate, POST /flags/deactivate, POST /damage, POST /heal

## Seed data (SQLite)
Create table: users(id INTEGER PRIMARY KEY, name TEXT, email TEXT, role TEXT)
Insert 10 users:
- id=1  alice   role=user
- id=2  bob     role=admin
- id=3  charlie role=user
- id=4  diana   role=user
- id=5  eve     role=admin
- id=6  frank   role=user
- id=7  grace   role=user
- id=8  henry   role=user
- id=9  iris    role=user
- id=10 jack    role=user

## Rules
- All vulnerabilities start INACTIVE
- Use SQLite (sqlite3 built-in — no extra DB needed)
- Create and seed DB on startup if not exists
- Scope is small — 2 vulns, keep it focused

## Files to deliver
- app.py
- requirements.txt
- Dockerfile — FROM python:3.11-slim, expose 8004, CMD ["python3","app.py"]

## Test your server
```bash
docker build -t db-server . && docker run -p 8004:8004 -e HACKATHON_SECRET=HACKATHON_SECRET_2025 db-server

# Search (safe)
curl -X POST http://localhost:8004/query -H "Content-Type: application/json" -d '{"search":"alice"}'

# Activate sqli
curl -X POST http://localhost:8004/flags/activate -H "Content-Type: application/json" -d '{"vuln":"sqli","secret":"HACKATHON_SECRET_2025"}'

# Test SQLi (should dump all users)
curl -X POST http://localhost:8004/query -H "Content-Type: application/json" -d '{"search":"'"'"' OR '"'"'1'"'"'='"'"'1'"'"' --"}'
```