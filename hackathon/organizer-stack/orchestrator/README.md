# Orchestrator — Team E (Members 7 & 8)

## What you are building
The brain of the entire platform. Runs on port 9000.
Controls vulnerability rotation, tracks HP, receives events, calculates scores.

## Port
9000

## Rotation schedule
- 4 slots, 450 seconds each = 30 minutes total
- Order: Web → API → File → DB
- All vulns start INACTIVE
- On each rotation: freeze current server HP → deactivate its vulns → activate next server vulns

## Vuln list per service
```python
SLOT_VULNS = {
    "web":  ["sqli","xss","auth_bypass"],
    "api":  ["insecure_ep","cmd_inject","idor"],
    "file": ["path_traversal","exec_upload"],
    "db":   ["sqli","priv_esc"],
}
```

## Internal Docker hostnames (use these, NOT LAN IPs)
Each service is reachable inside Docker by container name:
- team1-web:8001, team1-api:8002, team1-file:8003, team1-db:8004, team1-proxy
- team2-web:8001, team2-api:8002 ... (same pattern up to team10)

## Endpoints to implement

### Team registration
POST /register — body: {"team_id":1,"team_name":"Team 1","proxy_port":9100}
→ {"ok":true}
Initialize HP for this team: web=40, api=30, file=30, db=30

### Battle control
POST /battle/start → start rotation scheduler, activate web vulns on all teams
POST /battle/stop → stop scheduler, return final scores
GET /current → {"battle_started":bool,"active_service":"web","slot":1,"elapsed_seconds":120,"remaining_seconds":330,"battle_elapsed":120,"battle_remaining":1680}

### Team data
GET /teams → {"teams":[{"team_id":1,"name":"Team 1","proxy_port":9100},...]}
GET /hp → {"1":{"web":{"current":38,"max":40,"frozen":true},...},...}
GET /scores → {"scores":{"1":{"team_name":"Team 1","hp_score":35,"attack_score":18,"defense_score":12,"penalty":0,"total":65},...}}

### Events
POST /events — body: {"type":"exploit_success","source_team_id":"1","target_proxy_url":"http://192.168.1.100:9101","vuln":"sqli","hp_delta":-8}
→ On exploit_success: call POST http://teamN-web:8001/damage with amount=abs(hp_delta)
→ Append to events list (max 500)
GET /events → {"events":[...last 100...]}

### Admin overrides (require secret header)
POST /admin/set_hp — body: {"team_id":1,"service":"web","hp":25,"secret":"..."}
POST /admin/set_score — body: {"team_id":1,"score":88.5,"secret":"..."}
POST /admin/rename_team — body: {"team_id":1,"name":"New Name","secret":"..."}
DELETE /admin/remove_team — body: {"team_id":1,"secret":"..."}

### SSE stream
GET /stream — push every 2s:
{"battle_started":bool,"active_service":"web","remaining_seconds":330,"teams":[{"team_id":1,"name":"Team 1","hp":{"web":38,"api":30,"file":30,"db":30},"score":65.2}],"recent_events":[...last 10...]}

## Score formula
- hp_score = (sum of all current HP / sum of all max HP) × 40
- attack_score = min(successful_exploits × 2, 25)
- defense_score = min(successful_blocks × 2, 20)
- penalty = false_positives × -10
- total = hp_score + attack_score + defense_score + penalty

## Files to deliver
- orchestrator.py — complete Flask app + APScheduler
- requirements.txt — flask, flask-cors, requests, apscheduler, python-dotenv
- Dockerfile — python:3.11-slim, expose 9000, CMD ["python3","orchestrator.py"]

## Test
```bash
curl http://localhost:9000/current
curl -X POST http://localhost:9000/register -H "Content-Type: application/json" -d '{"team_id":1,"team_name":"Team 1","proxy_port":9100}'
curl -X POST http://localhost:9000/battle/start
```