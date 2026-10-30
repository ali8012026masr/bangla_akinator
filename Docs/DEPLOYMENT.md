# Bangla Akinator ("বাংলা জ্বিন") Production Deployment Guide

This document describes the end-to-end production deployment process for the Bangla Akinator game, encompassing containerized backend deployment, MongoDB Atlas cloud cluster management, Nginx reverse proxy configuration, and Flutter client builds (Android APK and Flutter Web).

---

## 1. System Architecture Overview

```
[ Android Client / Web Browser ]
             │ (HTTPS / TLS 1.3)
             ▼
      [ Nginx Reverse Proxy ]
      (SSL termination, Rate limiting)
             │ (HTTP internal port 8000)
             ▼
 [ FastAPI Backend (Docker Container) ]
      (PyMongo Async Engine, Lifespan Hooks)
             │ (TLS MongoDB Connection)
             ▼
  [ MongoDB Atlas / Local MongoDB 7.0 ]
   (Collections: characters, questions, sessions, contributions)
```

---

## 2. Backend Container Deployment (Docker & Compose)

### 2.1 Multi-Stage Dockerfile Features
The backend utilizes a multi-stage Docker build (`akinator_backend/Dockerfile`):
- **Builder Stage (`python:3.12-slim`)**: Compiles binary dependencies without carrying compiler tooling into production.
- **Runner Stage**: Runs under an unprivileged user (`appuser`, UID 1000) with minimal attack surface.
- **Built-in Healthcheck**: Probes `/health` every 30s.

### 2.2 Local & Staging Orchestration
Run the stack using Docker Compose:

```bash
# Build and run MongoDB 7.0 and FastAPI backend in background
docker compose up -d --build

# Inspect running services
docker compose ps

# View backend logs in real-time
docker compose logs -f backend

# Seed canonical Bengali dataset inside the backend container
docker compose exec backend python scripts/seed_data.py

# Run dataset validation check
docker compose exec backend python scripts/validate_seed_data.py
```

---

## 3. MongoDB Atlas Cloud Database Setup

For production, provision a managed replica set on [MongoDB Atlas](https://www.mongodb.com/cloud/atlas):

1. **Create Cluster**: Select M0 (Free Tier) or M10+ in AWS `ap-southeast-1` (Singapore) or `ap-south-1` (Mumbai) for low latency from Bangladesh.
2. **Database Access**: Create a secure user (e.g. `akinator_app`) with `readWrite` role on `bangla_akinator`.
3. **Network Access**: Add the static IP of your cloud VM / droplet to the IP Access List.
4. **Environment Configuration**:
   Update `MONGO_URI` in production `.env`:
   ```env
   MONGO_URI=mongodb+srv://akinator_app:<PASSWORD>@cluster0.abcde.mongodb.net/?retryWrites=true&w=majority
   DB_NAME=bangla_akinator
   LOG_LEVEL=INFO
   ```
5. **Index Provisioning**:
   The FastAPI lifespan automatically inspects and initializes all unique and TTL indexes upon startup:
   - `questions.question_code` (unique)
   - `characters.normalized_name` (unique)
   - `sessions.session_id` (unique)
   - `sessions.updated_at` (TTL index: 7200 seconds / 2 hours)

---

## 4. Reverse Proxy & SSL Configuration (Nginx)

Deploy Nginx on your production server with Certbot Let's Encrypt SSL:

```nginx
# Rate limiting zone (60 requests per minute per IP)
limit_req_zone $binary_remote_addr zone=akinator_api_limit:10m rate=60r/m;

server {
    listen 80;
    server_name api.bangla-akinator.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.bangla-akinator.com;

    ssl_certificate /etc/letsencrypt/live/api.bangla-akinator.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.bangla-akinator.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Security Headers
    add_header X-Content-Type-Options nosniff always;
    add_header X-Frame-Options DENY always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy strict-origin-when-cross-origin always;

    location / {
        limit_req zone=akinator_api_limit burst=20 nodelay;

        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts
        proxy_connect_timeout 10s;
        proxy_read_timeout 30s;
    }
}
```

---

## 5. Production CORS Whitelisting

In production, avoid wildcards (`*`) for CORS. Set `CORS_ORIGINS` in your environment or Docker Compose to only permit legitimate origins:

```env
CORS_ORIGINS=["https://bangla-akinator.com","https://play.bangla-akinator.com"]
```

---

## 6. Client Builds (Flutter)

### 6.1 Android Release Build (APK / AAB)

1. **Configure Signing**:
   Create `akinator_frontend/android/key.properties`:
   ```properties
   storePassword=<KEYSTORE_PASSWORD>
   keyPassword=<KEY_PASSWORD>
   keyAlias=upload
   storeFile=/path/to/keystore.jks
   ```

2. **Compile Release APK**:
   Pass the production API URL using `--dart-define`:
   ```bash
   cd akinator_frontend
   flutter build apk --release --dart-define=API_BASE_URL=https://api.bangla-akinator.com/api
   ```
   The resulting artifact is located at:
   `build/app/outputs/flutter-apk/app-release.apk`

3. **Compile App Bundle for Google Play (AAB)**:
   ```bash
   flutter build appbundle --release --dart-define=API_BASE_URL=https://api.bangla-akinator.com/api
   ```
   The resulting artifact is located at:
   `build/app/outputs/bundle/release/app-release.aab`

### 6.2 Flutter Web Release Build

1. **Compile for Web**:
   ```bash
   cd akinator_frontend
   flutter build web --release --dart-define=API_BASE_URL=https://api.bangla-akinator.com/api
   ```
2. **Deploy**:
   The output `akinator_frontend/build/web/` can be served directly from any static host:
   - **Firebase Hosting**: `firebase deploy --only hosting`
   - **Cloudflare Pages**: Connect git repo or upload `build/web`
   - **Nginx**: Point `root /var/www/bangla-akinator-web;` to the extracted files.

---

## 7. Operational Monitoring & Health Checks

- **Liveness probe**: `GET /health` returns `{"status":"ok"}` with HTTP 200.
- **Readiness probe**: `GET /ready` actively pings MongoDB and returns:
  ```json
  {
    "status": "ready",
    "database": "connected"
  }
  ```
- **Automated Alerts**: Configure uptime monitoring (Better Uptime, Pingdom, or UptimeRobot) targeting `https://api.bangla-akinator.com/ready`.
