# Workmate OS - Production Deployment Guide

## Prerequisites

- Server: workmate-01 (Ubuntu with Docker & Docker Compose installed)
- Domain: kit-it-koblenz.de (managed by Cloudflare)
- SSH access to the server
- Cloudflare account access for DNS configuration

## DNS Configuration (Cloudflare)

You need to create the following DNS records in Cloudflare:

| Type | Name | Content | Proxy Status |
|------|------|---------|--------------|
| A | workmate | [SERVER_IP] | DNS only (grey cloud) |
| A | api.workmate | [SERVER_IP] | DNS only (grey cloud) |
| A | traefik.workmate | [SERVER_IP] | DNS only (grey cloud) |

**Important:** The Proxy status MUST be set to "DNS only" (grey cloud) for Let's Encrypt HTTP-01 challenge to work!

To find your server IP:
```bash
ssh workmate-01 "curl -4 ifconfig.me"
```

## Step-by-Step Deployment

### 1. Configure Production Environment

Edit `infra/.env.prod` and replace all `CHANGE_ME` values:

```bash
# Generate secure secrets with:
openssl rand -base64 32

# Generate Traefik dashboard password:
htpasswd -nb admin YourPasswordHere
```

Update these variables:
- `POSTGRES_PASSWORD` - Strong database password
- `SECRET_KEY` - Random 32+ character secret
- `JWT_SECRET_KEY` - Random 32+ character secret
- `ACME_EMAIL` - Your email for Let's Encrypt notifications
- `TRAEFIK_DASHBOARD_AUTH` - Generated htpasswd string (keep $$)

### 2. Run Deployment Script

```bash
./deploy.sh
```

This script will:
1. Create deployment directory on server
2. Sync project files via rsync
3. Build and start Docker containers
4. Run database migrations
5. Display container status

### 3. Verify Deployment

Check services are running:
```bash
ssh workmate-01 "docker ps --filter 'name=workmate_'"
```

View logs:
```bash
ssh workmate-01 "docker logs -f workmate_backend"
ssh workmate-01 "docker logs -f workmate_frontend"
ssh workmate-01 "docker logs -f workmate_traefik"
```

### 4. Access the Application

After DNS propagation (usually 5-15 minutes):
- Frontend: https://workmate.kit-it-koblenz.de
- Backend API: https://api.workmate.kit-it-koblenz.de
- API Docs: https://api.workmate.kit-it-koblenz.de/docs
- Traefik Dashboard: https://traefik.workmate.kit-it-koblenz.de

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        workmate-01                          │
│                                                             │
│  ┌────────────┐       ┌──────────────┐                    │
│  │   Traefik  │◄──────┤  PostgreSQL  │                    │
│  │   (Proxy)  │       └──────────────┘                    │
│  └──────┬─────┘                                            │
│         │                                                   │
│    ┌────┴────┬─────────────────┐                          │
│    │         │                 │                          │
│    ▼         ▼                 ▼                          │
│  ┌────┐   ┌─────┐         ┌────┐                         │
│  │ UI │   │ API │         │ DB │                         │
│  │:80 │   │:8000│         │:5432                         │
│  └────┘   └─────┘         └────┘                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
         ▲               ▲               ▲
         │               │               │
    :443 HTTPS      :443 HTTPS      :443 HTTPS
         │               │               │
     workmate.*     api.workmate.*  traefik.workmate.*
```

## Container Details

### Backend (workmate_backend)
- Image: Custom Python 3.13 + FastAPI
- Workers: 4 uvicorn workers
- Port: 8000 (internal)
- Volumes: uploads_data, assets
- Database: PostgreSQL connection

### Frontend (workmate_frontend)
- Image: Custom Node 22 build + Nginx
- Port: 80 (internal)
- Static files served by Nginx
- SPA fallback routing enabled

### Database (workmate_postgres)
- Image: PostgreSQL 16 Alpine
- Port: 5432 (internal only)
- Volume: postgres_data (persistent)

### Traefik (workmate_traefik)
- Image: Traefik v3.2
- Ports: 80, 443 (exposed)
- Automatic SSL with Let's Encrypt
- Docker provider enabled
- Dashboard with basic auth

## Updating the Application

To deploy updates:
```bash
./deploy.sh
```

To rebuild containers without cache:
```bash
ssh workmate-01 "cd /opt/workmate/infra && docker compose -f docker-compose.prod.yml build --no-cache"
./deploy.sh
```

## Database Management

### Backup Database
```bash
ssh workmate-01 "docker exec workmate_postgres pg_dump -U workmate workmate_os > /tmp/backup.sql"
scp workmate-01:/tmp/backup.sql ./backup-$(date +%Y%m%d).sql
```

### Restore Database
```bash
scp backup.sql workmate-01:/tmp/
ssh workmate-01 "docker exec -i workmate_postgres psql -U workmate workmate_os < /tmp/backup.sql"
```

### Run Migrations
```bash
ssh workmate-01 "docker exec workmate_backend alembic upgrade head"
```

## Troubleshooting

### Check Container Logs
```bash
ssh workmate-01 "docker logs workmate_backend"
ssh workmate-01 "docker logs workmate_frontend"
ssh workmate-01 "docker logs workmate_traefik"
ssh workmate-01 "docker logs workmate_postgres"
```

### Restart Services
```bash
ssh workmate-01 "cd /opt/workmate/infra && docker compose -f docker-compose.prod.yml restart"
```

### Check SSL Certificates
```bash
ssh workmate-01 "docker exec workmate_traefik cat /letsencrypt/acme.json"
```

### Access Database Console
```bash
ssh workmate-01 "docker exec -it workmate_postgres psql -U workmate workmate_os"
```

### Check Traefik Dashboard
Visit: https://traefik.workmate.kit-it-koblenz.de
Login with credentials from `TRAEFIK_DASHBOARD_AUTH`

## Security Considerations

1. **Secrets**: Never commit `.env.prod` to git
2. **Firewall**: Only ports 80, 443, and SSH should be open
3. **SSH**: Use key-based authentication
4. **Database**: Not exposed externally (only internal Docker network)
5. **Traefik Dashboard**: Protected with basic auth
6. **Updates**: Regularly update Docker images and system packages

## Monitoring

Monitor the application health:
```bash
# Backend health check
curl https://api.workmate.kit-it-koblenz.de/system/health

# Frontend health check
curl https://workmate.kit-it-koblenz.de/health

# Docker stats
ssh workmate-01 "docker stats --no-stream"
```

## Backup Strategy

Recommended backup schedule:
- Database: Daily automated backups
- Uploads: Daily sync to Nextcloud (already configured)
- Configuration: Keep `.env.prod` in secure location

## Support

For issues, check:
1. Container logs
2. Traefik dashboard
3. Server resources (disk, memory, CPU)
4. DNS configuration
5. SSL certificate status
