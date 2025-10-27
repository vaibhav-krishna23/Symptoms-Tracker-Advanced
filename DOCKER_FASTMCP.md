# 🐳 Docker Deployment - FastMCP Version

## 📦 What Changed from Previous Version

### Before (3 Containers):
```
1. symptom-tracker-mcp  (port 8001) ← REMOVED
2. symptom-tracker-api  (port 8000)
3. symptom-tracker-web  (port 8501)
```

### After (2 Containers):
```
1. symptom-tracker-api  (port 8000) ← Now includes embedded FastMCP
2. symptom-tracker-web  (port 8501)
```

---

## 🚀 Quick Start

### 1. Build Images
```bash
# Windows
build-and-push.bat

# Linux/Mac
chmod +x build-and-push.sh
./build-and-push.sh
```

### 2. Run with Docker Compose
```bash
docker-compose up -d
```

### 3. Access Application
- **Frontend**: http://localhost:8501
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## 📋 Environment Variables

Create `.env` file in project root:

```env
# Database
DATABASE_URL=postgresql://user:pass@host:port/dbname
REDIS_URL=redis://default:pass@host:port

# Security
FERNET_KEY=your_fernet_key
JWT_SECRET_KEY=your_jwt_secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# AI
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.5-flash

# Email
SMTP_USER=your_email@gmail.com
SMTP_PASS=your_app_password
```

---

## 🔧 Docker Commands

### Build Images
```bash
# Build API image (FastAPI + FastMCP)
docker build -f Dockerfile.api -t vaibhavkrishna23/symptom-tracker-api:latest .

# Build Web image (Streamlit)
docker build -f Dockerfile.web -t vaibhavkrishna23/symptom-tracker-web:latest .
```

### Run Containers
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Restart services
docker-compose restart
```

### Manage Images
```bash
# List images
docker images | grep symptom-tracker

# Remove old images
docker rmi vaibhavkrishna23/symptom-tracker-mcp:latest

# Pull latest images
docker-compose pull
```

---

## 📊 Container Details

### API Container (symptom-fastapi)
- **Image**: `vaibhavkrishna23/symptom-tracker-api:latest`
- **Port**: 8000
- **Features**:
  - FastAPI REST API
  - Embedded FastMCP (spawns automatically)
  - LangGraph workflow
  - Google Gemini AI integration
- **Health Check**: `http://localhost:8000/health`

### Web Container (symptom-streamlit)
- **Image**: `vaibhavkrishna23/symptom-tracker-web:latest`
- **Port**: 8501
- **Features**:
  - Streamlit UI
  - Dark theme interface
  - Real-time symptom tracking
- **Health Check**: `http://localhost:8501/_stcore/health`

---

## 🔍 How FastMCP Works in Docker

### Inside API Container:
```
1. FastAPI starts on port 8000
2. When symptom request comes in:
   → FastAPI spawns FastMCP subprocess
   → FastMCP processes tools
   → Returns results
   → Subprocess terminates
3. No separate MCP container needed!
```

### Process View:
```bash
# Inside API container
docker exec -it symptom-fastapi ps aux

# You'll see:
# - uvicorn (main process)
# - python fastmcp_server.py (temporary, during requests)
```

---

## 🐛 Troubleshooting

### Check Container Status
```bash
docker-compose ps
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f fastapi
docker-compose logs -f streamlit
```

### Restart Services
```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart fastapi
```

### Check Health
```bash
# API health
curl http://localhost:8000/health

# Streamlit health
curl http://localhost:8501/_stcore/health
```

### Common Issues

#### 1. Port Already in Use
```bash
# Check what's using the port
netstat -ano | findstr :8000
netstat -ano | findstr :8501

# Kill the process or change port in docker-compose.yml
```

#### 2. Database Connection Failed
- Check `DATABASE_URL` in `.env`
- Ensure Railway database is accessible
- Check firewall settings

#### 3. FastMCP Subprocess Fails
- Check container logs: `docker-compose logs fastapi`
- Verify all dependencies installed
- Check Python version (should be 3.11+)

---

## 📦 Push to Docker Hub

### Login
```bash
docker login
```

### Tag Images
```bash
docker tag symptom-tracker-api:latest vaibhavkrishna23/symptom-tracker-api:v2.0.0-fastmcp
docker tag symptom-tracker-web:latest vaibhavkrishna23/symptom-tracker-web:v2.0.0-fastmcp
```

### Push Images
```bash
docker push vaibhavkrishna23/symptom-tracker-api:latest
docker push vaibhavkrishna23/symptom-tracker-api:v2.0.0-fastmcp
docker push vaibhavkrishna23/symptom-tracker-web:latest
docker push vaibhavkrishna23/symptom-tracker-web:v2.0.0-fastmcp
```

---

## 🚀 Production Deployment

### Using Docker Compose
```bash
# Production mode
docker-compose -f docker-compose.yml up -d

# With custom env file
docker-compose --env-file .env.production up -d
```

### Using Docker Swarm
```bash
docker stack deploy -c docker-compose.yml symptom-tracker
```

### Using Kubernetes
See `k8s/` directory for Kubernetes manifests (if available)

---

## 📊 Resource Requirements

### Minimum:
- **CPU**: 2 cores
- **RAM**: 2GB
- **Disk**: 5GB

### Recommended:
- **CPU**: 4 cores
- **RAM**: 4GB
- **Disk**: 10GB

---

## 🔒 Security Notes

- Never commit `.env` file to Git
- Use Docker secrets for production
- Enable HTTPS with reverse proxy (nginx/traefik)
- Regularly update base images
- Scan images for vulnerabilities: `docker scan`

---

## 📚 Additional Resources

- **Docker Compose Docs**: https://docs.docker.com/compose/
- **FastMCP**: https://github.com/jlowin/fastmcp
- **FastAPI**: https://fastapi.tiangolo.com/
- **Streamlit**: https://streamlit.io/

---

**Version**: 2.0.0-fastmcp  
**Last Updated**: 2024  
**Architecture**: 2 containers (API+FastMCP, Web)
