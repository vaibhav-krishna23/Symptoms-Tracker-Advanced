# 🚂 Railway Deployment Guide

## Prerequisites
- Railway account (https://railway.app)
- Docker images pushed to Docker Hub
- GitHub repository

## Step-by-Step Deployment

### 1. Create Railway Project

1. Go to https://railway.app
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Connect your GitHub account
5. Select: `vaibhav-krishna23/Symptoms-Tracker-Advanced`

### 2. Add PostgreSQL Database

1. In your Railway project, click "New"
2. Select "Database" → "PostgreSQL"
3. Railway will automatically create the database
4. Copy the `DATABASE_URL` from the database service

### 3. Deploy MCP Server

1. Click "New" → "Empty Service"
2. Name it: `mcp-server`
3. Go to "Settings" → "Source"
4. Select "Docker Image"
5. Enter: `vaibhav547/symptom-tracker-mcp:latest`
6. Go to "Variables" and add:
   ```
   DATABASE_URL=${{Postgres.DATABASE_URL}}
   GEMINI_API_KEY=your_gemini_key
   SMTP_USER=your_email@gmail.com
   SMTP_PASS=your_app_password
   FERNET_KEY=your_fernet_key
   JWT_SECRET_KEY=your_jwt_secret
   JWT_ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=1440
   GEMINI_MODEL=gemini-2.0-flash-exp
   MCP_SERVER_HOST=0.0.0.0
   MCP_SERVER_PORT=8001
   PORT=8001
   ```
7. Go to "Settings" → "Networking"
8. Click "Generate Domain" (you'll get: `mcp-server.railway.app`)

### 4. Deploy FastAPI Backend

1. Click "New" → "Empty Service"
2. Name it: `fastapi`
3. Go to "Settings" → "Source"
4. Select "Docker Image"
5. Enter: `vaibhav547/symptom-tracker-api:latest`
6. Go to "Variables" and add:
   ```
   DATABASE_URL=${{Postgres.DATABASE_URL}}
   GEMINI_API_KEY=your_gemini_key
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   SMTP_USER=your_email@gmail.com
   SMTP_PASS=your_app_password
   FERNET_KEY=your_fernet_key
   JWT_SECRET_KEY=your_jwt_secret
   JWT_ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=1440
   GEMINI_MODEL=gemini-2.0-flash-exp
   MCP_SERVER_HOST=mcp-server.railway.internal
   MCP_SERVER_PORT=8001
   ENV=production
   PORT=8000
   ```
7. Go to "Settings" → "Networking"
8. Click "Generate Domain" (you'll get: `fastapi.railway.app`)

### 5. Deploy Streamlit Frontend

1. Click "New" → "Empty Service"
2. Name it: `streamlit`
3. Go to "Settings" → "Source"
4. Select "Docker Image"
5. Enter: `vaibhav547/symptom-tracker-web:latest`
6. Go to "Variables" and add:
   ```
   API_BASE=https://your-fastapi-url.railway.app
   PORT=8501
   ```
   (Replace `your-fastapi-url` with the actual FastAPI domain from step 4)
7. Go to "Settings" → "Networking"
8. Click "Generate Domain" (you'll get: `streamlit.railway.app`)

### 6. Add Sample Doctor

Once deployed, add a doctor to the database:

**Option A: Using Railway CLI**
```bash
railway run python -c "
import sys
sys.path.append('.')
from app.db.session import SessionLocal
from app import crud

db = SessionLocal()
doctor = crud.create_doctor(
    db,
    full_name='Dr. Sarah Johnson',
    specialization='General Practitioner',
    clinic_name='City Health Clinic',
    city='New York',
    contact_email='doctor@example.com'
)
print(f'Doctor created: {doctor.doctor_id}')
db.close()
"
```

**Option B: Using FastAPI Docs**
1. Go to `https://your-fastapi-url.railway.app/docs`
2. Use `/api/v1/admin/doctors` POST endpoint
3. Add doctor details

### 7. Test the Application

1. Open: `https://your-streamlit-url.railway.app`
2. Register a new account
3. Login
4. Test symptom logging
5. Test photo upload
6. Test emergency appointment booking

## Environment Variables Reference

### Required for All Services:
```
DATABASE_URL - PostgreSQL connection string
GEMINI_API_KEY - Google Gemini API key
SMTP_USER - Gmail address
SMTP_PASS - Gmail app password
FERNET_KEY - Encryption key
JWT_SECRET_KEY - JWT signing key
```

### Generate Keys:
```python
# Fernet Key
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())

# JWT Secret
import secrets
print(secrets.token_urlsafe(32))
```

## Railway CLI Deployment (Alternative)

### Install Railway CLI:
```bash
npm install -g @railway/cli
```

### Login:
```bash
railway login
```

### Link Project:
```bash
railway link
```

### Deploy Services:
```bash
# Deploy MCP Server
railway up --service mcp-server --dockerfile Dockerfile.mcp

# Deploy FastAPI
railway up --service fastapi --dockerfile Dockerfile.api

# Deploy Streamlit
railway up --service streamlit --dockerfile Dockerfile.web
```

## Troubleshooting

### Service won't start:
- Check logs: Click on service → "Deployments" → "View Logs"
- Verify environment variables are set correctly
- Ensure DATABASE_URL is correct

### Database connection error:
- Make sure PostgreSQL service is running
- Check DATABASE_URL format: `postgresql://user:pass@host:port/db`
- Verify network connectivity between services

### MCP Server not reachable:
- Use internal URL: `mcp-server.railway.internal:8001`
- Don't use public domain for internal communication

### Photo upload not working:
- Railway has ephemeral storage
- Consider using AWS S3 or Cloudinary for production

## Cost Estimation

Railway Free Tier:
- $5 credit per month
- ~500 execution hours
- Enough for development/testing

Estimated usage:
- 3 services × 24 hours × 30 days = 2,160 hours
- Cost: ~$10-15/month (beyond free tier)

## Production Recommendations

1. **Use S3 for photo storage** (Railway storage is ephemeral)
2. **Enable health checks** for all services
3. **Set up monitoring** and alerts
4. **Use Redis** for caching (add Redis service)
5. **Enable auto-scaling** for high traffic
6. **Set up custom domain** for professional look

## Useful Commands

```bash
# View logs
railway logs --service mcp-server
railway logs --service fastapi
railway logs --service streamlit

# Restart service
railway restart --service fastapi

# Check status
railway status

# Open service URL
railway open
```

## Support

- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- Project Issues: https://github.com/vaibhav-krishna23/Symptoms-Tracker-Advanced/issues
