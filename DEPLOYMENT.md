# Deployment Guide

This guide covers different deployment options for the Vulnerability Scanner Web Application.

## Table of Contents
- [Docker Deployment](#docker-deployment)
- [Manual Deployment](#manual-deployment)
- [Production Considerations](#production-considerations)
- [Cloud Deployment](#cloud-deployment)

---

## Docker Deployment

### Prerequisites
- Docker (v20.10+)
- Docker Compose (v2.0+)

### Quick Start with Docker

1. **Clone the repository**
```bash
git clone https://github.com/aryansinghshaktawat/vuln-scanner-webapp.git
cd vuln-scanner-webapp
```

2. **Build and run with Docker Compose**
```bash
docker-compose up -d
```

3. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

4. **View logs**
```bash
# All services
docker-compose logs -f

# Backend only
docker-compose logs -f backend

# Frontend only
docker-compose logs -f frontend
```

5. **Stop the application**
```bash
docker-compose down
```

### Building Individual Images

**Backend:**
```bash
cd backend
docker build -t vuln-scanner-backend .
docker run -p 8000:8000 vuln-scanner-backend
```

**Frontend:**
```bash
cd frontend
docker build -t vuln-scanner-frontend .
docker run -p 3000:3000 vuln-scanner-frontend
```

---

## Manual Deployment

### Production Backend Setup

1. **Server Requirements**
   - Ubuntu 20.04+ or similar Linux distribution
   - Python 3.8+
   - Nmap installed
   - Nginx (optional, for reverse proxy)

2. **Install dependencies**
```bash
# System packages
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv nmap nginx

# Clone repository
git clone https://github.com/aryansinghshaktawat/vuln-scanner-webapp.git
cd vuln-scanner-webapp/backend

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install Python packages
pip install -r requirements.txt
```

3. **Configure environment**
```bash
cp .env.example .env
# Edit .env with production settings
nano .env
```

4. **Run with systemd (recommended)**

Create `/etc/systemd/system/vuln-scanner-backend.service`:
```ini
[Unit]
Description=Vulnerability Scanner Backend
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/vuln-scanner-webapp/backend
Environment="PATH=/path/to/vuln-scanner-webapp/backend/.venv/bin"
ExecStart=/path/to/vuln-scanner-webapp/backend/.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable vuln-scanner-backend
sudo systemctl start vuln-scanner-backend
sudo systemctl status vuln-scanner-backend
```

### Production Frontend Setup

1. **Install Node.js**
```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

2. **Build the application**
```bash
cd frontend
npm install
npm run build
```

3. **Run with PM2 (recommended)**
```bash
# Install PM2
sudo npm install -g pm2

# Start the application
pm2 start npm --name "vuln-scanner-frontend" -- start

# Save PM2 configuration
pm2 save

# Setup PM2 to start on boot
pm2 startup
```

---

## Production Considerations

### Security

1. **Environment Variables**
   - Never commit `.env` files
   - Use strong secrets for production
   - Limit CORS origins to your domain

2. **Firewall Configuration**
```bash
# Allow only necessary ports
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable
```

3. **Nginx Reverse Proxy**

Create `/etc/nginx/sites-available/vuln-scanner`:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/vuln-scanner /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

4. **SSL Certificate with Let's Encrypt**
```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### Performance

1. **Backend Optimization**
   - Use Gunicorn with multiple workers
   ```bash
   pip install gunicorn
   gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
   ```

2. **Frontend Optimization**
   - Enable Next.js caching
   - Use CDN for static assets
   - Enable gzip compression in Nginx

3. **Rate Limiting**
   - Implement rate limiting in Nginx or application level
   - Prevent abuse of scanning endpoints

### Monitoring

1. **Logging**
   - Configure application logs to `/var/log/vuln-scanner/`
   - Use log rotation with logrotate
   - Monitor with tools like ELK stack or Grafana

2. **Health Checks**
```bash
# Check backend health
curl http://localhost:8000/

# Check frontend
curl http://localhost:3000/
```

3. **Monitoring Tools**
   - Prometheus + Grafana for metrics
   - Uptime monitoring with UptimeRobot
   - Application Performance Monitoring (APM)

---

## Cloud Deployment

### AWS Deployment

**Option 1: EC2 Instance**
1. Launch Ubuntu EC2 instance (t2.medium or larger)
2. Configure security groups (ports 22, 80, 443)
3. Follow manual deployment steps above
4. Use Elastic IP for static IP address

**Option 2: ECS with Fargate**
1. Push Docker images to ECR
2. Create ECS task definitions
3. Deploy with Fargate
4. Use Application Load Balancer

**Option 3: Elastic Beanstalk**
1. Package application
2. Deploy using EB CLI
3. Configure environment variables

### Google Cloud Platform

**Option 1: Compute Engine**
1. Create VM instance
2. Follow manual deployment steps
3. Use Cloud Load Balancing

**Option 2: Cloud Run**
1. Build and push Docker images to GCR
2. Deploy containers to Cloud Run
3. Configure custom domains

### DigitalOcean

**Option 1: Droplet**
1. Create Ubuntu droplet
2. Follow manual deployment steps
3. Use floating IP

**Option 2: App Platform**
1. Connect GitHub repository
2. Configure build settings
3. Deploy automatically

### Heroku

**Backend:**
```bash
# Install Heroku CLI
heroku login
heroku create vuln-scanner-backend

# Add buildpack
heroku buildpacks:set heroku/python

# Add Nmap buildpack
heroku buildpacks:add https://github.com/wagonli/heroku-buildpack-nmap.git

# Deploy
git subtree push --prefix backend heroku main
```

**Frontend:**
```bash
heroku create vuln-scanner-frontend
cd frontend
git init
git add .
git commit -m "Initial commit"
heroku git:remote -a vuln-scanner-frontend
git push heroku main
```

---

## Environment Variables Reference

### Backend (.env)
```
HOST=0.0.0.0
PORT=8000
CORS_ORIGINS=https://your-domain.com
BASIC_SCAN_TIMEOUT=180
VULN_SCAN_TIMEOUT=300
LOG_LEVEL=INFO
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=https://api.your-domain.com
NEXT_PUBLIC_APP_NAME=Vulnerability Scanner
```

---

## Backup and Maintenance

### Backup Strategy
1. **Application Code**: Use Git
2. **Configuration**: Backup `.env` files securely
3. **Logs**: Regular log archival

### Updates
```bash
# Pull latest changes
git pull origin main

# Backend
cd backend
source .venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart vuln-scanner-backend

# Frontend
cd frontend
npm install
npm run build
pm2 restart vuln-scanner-frontend
```

---

## Troubleshooting

### Common Issues

**Backend not starting:**
```bash
# Check logs
journalctl -u vuln-scanner-backend -f

# Verify Nmap installation
which nmap
nmap --version
```

**Frontend build errors:**
```bash
# Clear cache and rebuild
rm -rf .next node_modules
npm install
npm run build
```

**Docker issues:**
```bash
# View container logs
docker-compose logs backend
docker-compose logs frontend

# Restart containers
docker-compose restart

# Rebuild from scratch
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

---

## Support

For issues or questions:
- GitHub Issues: https://github.com/aryansinghshaktawat/vuln-scanner-webapp/issues
- Email: your-email@example.com

---

**Last Updated:** November 2025
