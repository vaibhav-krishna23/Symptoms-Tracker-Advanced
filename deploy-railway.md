# 🚀 Quick Railway Deployment

## Method 1: Railway Dashboard (Easiest)

### Step 1: Create Project
1. Go to https://railway.app/new
2. Click "Deploy from Docker Image"

### Step 2: Deploy 3 Services

**Service 1: MCP Server**
- Image: `vaibhav547/symptom-tracker-mcp:latest`
- Port: `8001`
- Generate domain

**Service 2: FastAPI**
- Image: `vaibhav547/symptom-tracker-api:latest`
- Port: `8000`
- Generate domain

**Service 3: Streamlit**
- Image: `vaibhav547/symptom-tracker-web:latest`
- Port: `8501`
- Generate domain

### Step 3: Add PostgreSQL
- Click "New" → "Database" → "PostgreSQL"

### Step 4: Set Environment Variables

**MCP Server:**
```
DATABASE_URL=${{Postgres.DATABASE_URL}}
GEMINI_API_KEY=<your_key>
SMTP_USER=<your_email>
SMTP_PASS=<your_app_password>
FERNET_KEY=<your_fernet_key>
JWT_SECRET_KEY=<your_jwt_secret>
PORT=8001
```

**FastAPI:**
```
DATABASE_URL=${{Postgres.DATABASE_URL}}
GEMINI_API_KEY=<your_key>
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=<your_email>
SMTP_PASS=<your_app_password>
FERNET_KEY=<your_fernet_key>
JWT_SECRET_KEY=<your_jwt_secret>
MCP_SERVER_HOST=mcp-server.railway.internal
MCP_SERVER_PORT=8001
PORT=8000
```

**Streamlit:**
```
API_BASE=https://<your-fastapi-domain>.railway.app
PORT=8501
```

### Step 5: Access Your App
- Streamlit URL: `https://<your-streamlit-domain>.railway.app`

---

## Method 2: Railway CLI

### Install CLI:
```bash
npm install -g @railway/cli
```

### Deploy:
```bash
railway login
railway init
railway add --database postgres

# Set environment variables in Railway dashboard
# Then deploy will happen automatically
```

---

## Generate Required Keys

### Fernet Key:
```python
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
```

### JWT Secret:
```python
import secrets
print(secrets.token_urlsafe(32))
```

---

## After Deployment

### Add a Doctor:
Go to: `https://<your-fastapi-domain>.railway.app/docs`

Use endpoint: `POST /api/v1/admin/doctors`

Body:
```json
{
  "full_name": "Dr. Sarah Johnson",
  "specialization": "General Practitioner",
  "clinic_name": "City Health Clinic",
  "city": "New York",
  "contact_email": "doctor@example.com",
  "contact_number": "+1234567890"
}
```

---

## Your Docker Images

- MCP: `vaibhav547/symptom-tracker-mcp:latest`
- API: `vaibhav547/symptom-tracker-api:latest`
- Web: `vaibhav547/symptom-tracker-web:latest`

---

## Estimated Cost

- Free tier: $5/month credit
- 3 services running 24/7: ~$10-15/month
- First month mostly free with credits

---

## Need Help?

Check full guide: `RAILWAY_DEPLOYMENT.md`
