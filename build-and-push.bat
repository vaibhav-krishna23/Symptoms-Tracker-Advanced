@echo off

REM Docker Hub username
SET DOCKER_USERNAME=vaibhav547

REM Image version
SET VERSION=latest

echo 🐳 Building Docker images...

REM Build MCP Server
echo Building MCP Server...
docker build -f Dockerfile.mcp -t %DOCKER_USERNAME%/symptom-tracker-mcp:%VERSION% .

REM Build FastAPI
echo Building FastAPI...
docker build -f Dockerfile.api -t %DOCKER_USERNAME%/symptom-tracker-api:%VERSION% .

REM Build Streamlit
echo Building Streamlit...
docker build -f Dockerfile.web -t %DOCKER_USERNAME%/symptom-tracker-web:%VERSION% .

echo ✅ All images built successfully!

echo 🚀 Pushing images to Docker Hub...

REM Login to Docker Hub
echo Please login to Docker Hub:
docker login

REM Push images
docker push %DOCKER_USERNAME%/symptom-tracker-mcp:%VERSION%
docker push %DOCKER_USERNAME%/symptom-tracker-api:%VERSION%
docker push %DOCKER_USERNAME%/symptom-tracker-web:%VERSION%

echo ✅ All images pushed to Docker Hub!
echo.
echo 📦 Images available at:
echo    - %DOCKER_USERNAME%/symptom-tracker-mcp:%VERSION%
echo    - %DOCKER_USERNAME%/symptom-tracker-api:%VERSION%
echo    - %DOCKER_USERNAME%/symptom-tracker-web:%VERSION%

pause
