# 🚀 Render Deployment Guide

## Docker Images Built

All 3 services are containerized and pushed to Docker Hub:

- **MCP Server**: `vaibhav547/symptoms_tracker_advanced:mcp-latest`
- **API Backend**: `vaibhav547/symptoms_tracker_advanced:api-latest`  
- **Web Frontend**: `vaibhav547/symptoms_tracker_advanced:web-latest`

## Render Deployment Steps

### 1. MCP Server (Real MCP with SSE)
- **Service Type**: Web Service
- **Docker Image**: `vaibhav547/symptoms_tracker_advanced:mcp-latest`
- **Port**: 8001
- **Health Check**: `/health`

**Environment Variables:**
```
DATABASE_URL=postgresql://postgres:NIjvEejhRAmyBSVEsKLVxLdHToasBjfw@turntable.proxy.rlwy.net:12989/railway
REDIS_URL=redis://default:EBtAsngcNVrhcJNwsPGzaxTUArPDJqon@centerbeam.proxy.rlwy.net:22174
FERNET_KEY=StnBgHgsFrTEftGXOsWwfk4Zq8d31fLIiI8E4AVrgXc=
JWT_SECRET_KEY=supersecretjwtkey
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
GEMINI_API_KEY=AIzaSyC0AHUzcDBh2yKy7N39bzXNPqg3isPLg3c
GEMINI_MODEL=gemini-2.5-flash
GEMINI_API_BASE=https://generativelanguage.googleapis.com/v1beta
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=vaibhavtowardsdawn@gmail.com
SMTP_PASS=ezyfpilruvwltcxp
ENV=production
```

### 2. FastAPI Backend
- **Service Type**: Web Service
- **Docker Image**: `vaibhav547/symptoms_tracker_advanced:api-latest`
- **Port**: 8000
- **Health Check**: `/health`

**Environment Variables:** (Same as above)

### 3. Streamlit Frontend
- **Service Type**: Web Service
- **Docker Image**: `vaibhav547/symptoms_tracker_advanced:web-latest`
- **Port**: 8501
- **Health Check**: `/health` (if available)

**Environment Variables:**
```
API_BASE=https://your-api-service.onrender.com
MCP_BASE=https://your-mcp-service.onrender.com
```

## Service URLs

After deployment, you'll get URLs like:
- **MCP Server**: `https://symptoms-tracker-mcp.onrender.com`
- **API Backend**: `https://symptoms-tracker-api.onrender.com`
- **Web Frontend**: `https://symptoms-tracker-web.onrender.com`

## Update Frontend Configuration

After getting the API and MCP URLs, update the Streamlit app configuration to point to the deployed services instead of localhost.

## Architecture

```
Internet → Streamlit (Port 8501) → FastAPI (Port 8000) → MCP Server (Port 8001) → Database
```

## Features

✅ **Real MCP Protocol**: Official Anthropic MCP with SSE transport  
✅ **Production Ready**: All services containerized and scalable  
✅ **Health Checks**: Built-in health endpoints for monitoring  
✅ **Environment Variables**: Secure configuration management  
✅ **Photo Upload**: Symptom photos with email attachments  
✅ **AI Analysis**: Google Gemini 2.5 Flash integration  
✅ **Email Notifications**: SMTP with photo attachments  

## Troubleshooting

1. **Service won't start**: Check environment variables
2. **Database connection**: Verify DATABASE_URL
3. **Email not working**: Check SMTP credentials
4. **MCP tools failing**: Verify MCP server is running on port 8001
5. **Photo upload issues**: Check uploads directory permissions

## Monitoring

- Check `/health` endpoints for all services
- Monitor Render logs for errors
- Verify database connections
- Test email functionality