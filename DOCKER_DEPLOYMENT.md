# 🐳 Docker Deployment Guide

## Docker Images

This project consists of 3 Docker images:

1. **symptom-tracker-mcp** - MCP Server (Port 8001)
2. **symptom-tracker-api** - FastAPI Backend (Port 8000)
3. **symptom-tracker-web** - Streamlit Frontend (Port 8501)

## Prerequisites

- Docker installed
- Docker Hub account
- Environment variables configured

## Build and Push to Docker Hub

### Windows:
```bash
build-and-push.bat
```

### Linux/Mac:
```bash
chmod +x build-and-push.sh
./build-and-push.sh
```

### Manual Build:
```bash
# Build images
docker build -f Dockerfile.mcp -t vaibhavkrishna23/symptom-tracker-mcp:latest .
docker build -f Dockerfile.api -t vaibhavkrishna23/symptom-tracker-api:latest .
docker build -f Dockerfile.web -t vaibhavkrishna23/symptom-tracker-web:latest .

# Login to Docker Hub
docker login

# Push images
docker push vaibhavkrishna23/symptom-tracker-mcp:latest
docker push vaibhavkrishna23/symptom-tracker-api:latest
docker push vaibhavkrishna23/symptom-tracker-web:latest
```

## Run Locally with Docker Compose

### 1. Create `.env` file:
```env
DATABASE_URL=postgresql://user:password@host:5432/dbname
GEMINI_API_KEY=your_gemini_key
SMTP_USER=your_email@gmail.com
SMTP_PASS=your_app_password
FERNET_KEY=your_fernet_key
JWT_SECRET_KEY=your_jwt_secret
```

### 2. Start all services:
```bash
docker-compose up -d
```

### 3. Access application:
- **Streamlit UI:** http://localhost:8501
- **FastAPI Docs:** http://localhost:8000/docs
- **MCP Server:** http://localhost:8001

### 4. Stop services:
```bash
docker-compose down
```

## Deploy to Railway

### Using Docker Images:

1. **Create Railway Project:**
   ```bash
   railway init
   ```

2. **Add PostgreSQL:**
   ```bash
   railway add --database postgres
   ```

3. **Deploy MCP Server:**
   ```bash
   railway up --image vaibhavkrishna23/symptom-tracker-mcp:latest
   ```

4. **Deploy FastAPI:**
   ```bash
   railway up --image vaibhavkrishna23/symptom-tracker-api:latest
   ```

5. **Deploy Streamlit:**
   ```bash
   railway up --image vaibhavkrishna23/symptom-tracker-web:latest
   ```

6. **Set Environment Variables** in Railway Dashboard

## Deploy to Render

1. Create 3 Web Services
2. Use Docker image deployment
3. Set image URLs:
   - `vaibhavkrishna23/symptom-tracker-mcp:latest`
   - `vaibhavkrishna23/symptom-tracker-api:latest`
   - `vaibhavkrishna23/symptom-tracker-web:latest`
4. Configure environment variables

## Deploy to AWS ECS/Fargate

```bash
# Push to AWS ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Tag images
docker tag vaibhavkrishna23/symptom-tracker-mcp:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/symptom-tracker-mcp:latest
docker tag vaibhavkrishna23/symptom-tracker-api:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/symptom-tracker-api:latest
docker tag vaibhavkrishna23/symptom-tracker-web:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/symptom-tracker-web:latest

# Push to ECR
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/symptom-tracker-mcp:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/symptom-tracker-api:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/symptom-tracker-web:latest
```

## Environment Variables

### All Services:
```
DATABASE_URL=postgresql://...
GEMINI_API_KEY=...
SMTP_USER=...
SMTP_PASS=...
FERNET_KEY=...
JWT_SECRET_KEY=...
```

### FastAPI Service:
```
MCP_SERVER_HOST=mcp-server
MCP_SERVER_PORT=8001
```

### Streamlit Service:
```
API_BASE=http://fastapi:8000
```

## Troubleshooting

### Check logs:
```bash
docker-compose logs -f
```

### Rebuild images:
```bash
docker-compose build --no-cache
```

### Remove all containers:
```bash
docker-compose down -v
```

## Docker Hub Links

- MCP Server: https://hub.docker.com/r/vaibhavkrishna23/symptom-tracker-mcp
- FastAPI: https://hub.docker.com/r/vaibhavkrishna23/symptom-tracker-api
- Streamlit: https://hub.docker.com/r/vaibhavkrishna23/symptom-tracker-web

## Image Sizes

- MCP Server: ~500MB
- FastAPI: ~500MB
- Streamlit: ~500MB

## Security Notes

- Never commit `.env` file
- Use secrets management in production
- Rotate keys regularly
- Use private Docker registry for sensitive apps
