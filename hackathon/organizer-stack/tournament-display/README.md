# Tournament Display — Team E (Members 7 & 8)

## What you are building
A read-only big-screen scoreboard on port 5000.
Opened by the display PC (TV/projector) at: http://192.168.1.100:5000
No controls — pure display only.

## Port
5000

## UI design (dark theme #0d1117, fullscreen, pure HTML/CSS/JS, no external dependencies)

### Top bar
- "CYBER BATTLE HACKATHON" in large cyan monospace font
- Battle elapsed timer: MM:SS / 30:00
- Active service name with pulsing CSS glow: text-shadow: 0 0 20px cyan

### Rotation progress bar
- 4 equal segments: WEB | API | FILE | DB
- Active = cyan fill + white text
- Completed = dim fill
- Upcoming = dark fill
- Shows time range: 0:00–7:30, 7:30–15:00, 15:00–22:30, 22:30–30:00

### Teams scoreboard (main area)
- Sorted by score descending, CSS transition on re-sort
- Up to 10 team cards in a responsive grid
- Each card:
  - Rank: 1=gold border glow, 2=silver, 3=bronze, rest=white
  - Team name (large)
  - Score (very large, bold, cyan)
  - 4 mini HP bars: WEB / API / FILE / DB — green >60%, yellow 30-60%, red <30%
  - Attack count (red) + Defense count (green)

### Bottom ticker
- Horizontal scrolling ticker (CSS @keyframes translateX loop, ~30s cycle)
- Last 15 events: "Team Alpha exploited SQLi on Team Beta (-8 HP)"
- Color coded by type

### Visual effects (CSS only)
- Background scanlines: repeating-linear-gradient subtle overlay
- Active service glow animation
- Score number smooth transition on change
- Auto-requests fullscreen on page load

## API endpoints (Flask, port 5000)
- GET / → serve display.html
- GET /stream → proxy SSE from orchestrator /stream

## Files to deliver
- app.py — Flask on port 5000
- requirements.txt — flask, flask-cors, requests
- Dockerfile — python:3.11-slim, expose 5000, CMD ["python3","app.py"]
- templates/display.html — complete tournament display UI