# Bot IDE — Team E (Members 7 & 8)

## What you are building
A web-based code editor (Monaco) that teams use in their browser to write and run their bots.
No installation needed on team machines — they just open a URL.

## How it works
- Each team opens: http://192.168.1.100:810X (X = team number, e.g. 8100 for team 1)
- They see a Monaco editor (same as VS Code) in their browser
- They write their attacker and defender bot in ANY language
- They click "Run" — code executes inside the container
- Output appears live in the log panel below

## Supported languages
| Language | File extension | Runtime |
|----------|---------------|---------|
| Python | .py | python3 |
| JavaScript | .js | node |
| Go | .go | go run |
| Java | .java | javac + java |
| C | .c | gcc + run |
| Bash | .sh | bash |

## Files to deliver

### ide_server.py
Flask app on port 8080 (mapped to 810X on host). Serves Monaco HTML and handles:
- GET /api/files — list files in /app/workspace
- GET /api/files/<filename> — read file content
- POST /api/files/<filename> — save file content
- POST /api/run/<bot_name> — run attacker or defender bot (detect language from extension)
- POST /api/stop/<bot_name> — kill running process
- GET /api/logs/<bot_name> — return stdout lines
- GET /api/context — return team info, enemy targets, orchestrator URL

### templates/ide.html
Single-page Monaco editor. Load Monaco from:
https://cdn.jsdelivr.net/npm/monaco-editor@0.45.0/min/vs

UI layout:
- Top bar: team name, language selector, Run button (green), Stop button (red), status dot
- Left sidebar: file list, New File button
- Center: Monaco editor (dark theme vs-dark)
- Bottom split: Attacker logs (left) | Defender logs (right) — auto-scroll, poll every 2s
- Info panel: shows MY target URL, orchestrator URL, enemy targets

### Dockerfile
```dockerfile
FROM ubuntu:22.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
    python3 python3-pip nodejs npm golang-go default-jdk gcc g++ make curl wget bash \
    && rm -rf /var/lib/apt/lists/*
RUN pip3 install requests flask flask-cors beautifulsoup4
RUN npm install -g axios
WORKDIR /app
COPY requirements.txt .
RUN pip3 install -r requirements.txt
COPY . .
RUN mkdir -p /app/workspace
EXPOSE 8080
CMD ["python3", "ide_server.py"]
```

### starter-bots/
Provide one starter file per language showing how to:
1. Read ORCHESTRATOR_URL, SERVER_IP, TEAM_ID from env vars
2. Call GET {ORCH}/teams to get enemy target list
3. Call GET {ORCH}/current to get active service
4. Send HTTP requests to enemy targets
5. Report results via POST {ORCH}/events

Files: attacker.py, attacker.js, attacker.go, attacker.java, attacker.c, attacker.sh

### Environment variables (already set by docker-compose)
- TEAM_ID — team number (1–10)
- TEAM_NAME — display name
- ORCHESTRATOR_URL — http://orchestrator:9000
- MY_PROXY_PORT — 9100–9109 (their own vulnerable server port)
- SERVER_IP — 192.168.1.100
- HACKATHON_SECRET — HACKATHON_SECRET_2025

### Key env vars teams can use in their bots
- TARGET — http://SERVER_IP:MY_PROXY_PORT (their own server, for testing)
- ORCH — http://orchestrator:9000
- SERVER_IP — to build enemy URLs: http://SERVER_IP:9101, :9102, etc.

## Test your IDE
```bash
docker build -t bot-ide . && docker run -p 8100:8080 \
  -e TEAM_ID=1 -e TEAM_NAME="Team 1" \
  -e ORCHESTRATOR_URL=http://localhost:9000 \
  -e MY_PROXY_PORT=9100 \
  -e SERVER_IP=192.168.1.100 \
  bot-ide

# Open browser: http://localhost:8100
```