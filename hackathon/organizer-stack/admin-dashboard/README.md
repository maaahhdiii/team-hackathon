# Admin Dashboard — Team E (Members 7 & 8)

## What you are building
A full CRUD web interface on port 4000 for the organizer.
Opened by the admin PC at: http://192.168.1.100:4000

## Port
4000

## What the organizer can do
- See all 10 teams in a grid with live HP bars and scores
- Start and stop the battle
- Edit any team's display name (click to edit inline)
- Manually set HP for any team's service (override)
- Manually set a team's total score (override)
- Remove a team from the battle
- See live event log (last 20 events, color coded)
- Open any team's Monaco IDE in a new tab

## UI layout (dark theme #0d1117, pure HTML/CSS/JS, no external dependencies except Monaco CDN)

### Top bar
- "Cyber Battle — Admin" title
- Battle status pill: green "ACTIVE" / gray "IDLE"
- Active service badge + slot countdown MM:SS
- Start Battle button (green) + Stop Battle button (red)

### Teams grid (2-column, auto-refresh via SSE every 3s)
Each team card shows:
- Team name (click to edit → blur saves)
- Team ID + proxy URL (e.g. http://192.168.1.100:9100)
- "Open IDE" button → opens http://192.168.1.100:810X in new tab
- HP bars for all 4 services (green >60%, yellow 30-60%, red <30%)
- Total score (large, bold)
- "Manage" toggle → expands controls:
  - Set HP: select service + number input + Set button
  - Set Score: number input + Set button
  - Remove team: red button + confirmation

### Event log (full width bottom)
- Last 20 events, color: exploit_success=red, block=green, patch=cyan, heal=teal
- Shows: time, source team, target team, vuln, hp_delta

## API endpoints (Flask, port 4000)
Thin proxy layer — forwards calls to orchestrator and adds secret header automatically.

- GET / → serve index.html
- GET /api/teams → merged team data (teams + hp + scores)
- POST /api/teams/rename → forward to orchestrator /admin/rename_team
- DELETE /api/teams/<team_id> → forward to /admin/remove_team
- POST /api/teams/<team_id>/hp → forward to /admin/set_hp
- POST /api/teams/<team_id>/score → forward to /admin/set_score
- POST /api/battle/start → forward to /battle/start
- POST /api/battle/stop → forward to /battle/stop
- GET /api/status → forward to /current
- GET /api/events → forward to /events
- GET /stream → proxy SSE from orchestrator /stream

## Files to deliver
- app.py — Flask on port 4000
- requirements.txt — flask, flask-cors, requests
- Dockerfile — python:3.11-slim, expose 4000, CMD ["python3","app.py"]
- templates/index.html — complete admin UI