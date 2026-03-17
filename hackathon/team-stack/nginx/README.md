# Nginx Reverse Proxy — Team E (Members 7 & 8)

## What you are building
A single Nginx reverse proxy that sits in front of all 4 vulnerable servers.
Port 80 is the ONLY public port. Bots always connect here.
The orchestrator updates which server is active by rewriting the upstream and reloading Nginx.

## How it works
- All 4 servers run on internal ports (8001, 8002, 8003, 8004)
- Nginx listens on port 80 and forwards to whichever server is currently active
- On each rotation, the orchestrator rewrites nginx.conf and calls: docker exec proxy nginx -s reload

## Files to deliver

### nginx.conf
```nginx
upstream active_service {
    server web-service:8001;  # ← orchestrator rewrites this line on rotation
}
server {
    listen 80;
    location / {
        proxy_pass http://active_service;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_connect_timeout 5s;
        proxy_read_timeout 30s;
    }
    location /nginx-health {
        return 200 '{"status":"ok"}';
        add_header Content-Type application/json;
    }
}
```

### Dockerfile
```dockerfile
FROM nginx:alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
```

## Rotation — what the orchestrator does on each slot change
```python
# Pseudocode — Team E does NOT implement this, orchestrator does
config = open('nginx.conf').read()
config = re.sub(r'server \S+:\d+;', f'server {next_service}:{next_port};', config)
open('nginx.conf','w').write(config)
os.system('docker exec proxy nginx -s reload')
```

## Test your proxy
```bash
docker build -t proxy . && docker run -p 80:80 proxy

# Health check
curl http://localhost/nginx-health
```