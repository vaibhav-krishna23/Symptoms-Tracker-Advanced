@echo off
REM Build and Push Docker Images for FastMCP Version
REM Version: 2.0.0-fastmcp

echo ========================================
echo Building Symptom Tracker Docker Images
echo Version: 2.0.0-fastmcp (FastMCP)
echo ========================================
echo.

REM Set your Docker Hub username
set DOCKER_USER=vaibhavkrishna23

REM Build API image (with embedded FastMCP)
echo [1/2] Building API image (FastAPI + FastMCP)...
docker build -f Dockerfile.api -t %DOCKER_USER%/symptom-tracker-api:latest -t %DOCKER_USER%/symptom-tracker-api:v2.0.0-fastmcp .
if %errorlevel% neq 0 (
    echo ERROR: API build failed!
    exit /b 1
)
echo ✓ API image built successfully
echo.

REM Build Web image
echo [2/2] Building Web image (Streamlit)...
docker build -f Dockerfile.web -t %DOCKER_USER%/symptom-tracker-web:latest -t %DOCKER_USER%/symptom-tracker-web:v2.0.0-fastmcp .
if %errorlevel% neq 0 (
    echo ERROR: Web build failed!
    exit /b 1
)
echo ✓ Web image built successfully
echo.

echo ========================================
echo All images built successfully!
echo ========================================
echo.

REM Ask to push
set /p PUSH="Push images to Docker Hub? (y/n): "
if /i "%PUSH%"=="y" (
    echo.
    echo Pushing images to Docker Hub...
    echo.
    
    echo Pushing API image...
    docker push %DOCKER_USER%/symptom-tracker-api:latest
    docker push %DOCKER_USER%/symptom-tracker-api:v2.0.0-fastmcp
    
    echo Pushing Web image...
    docker push %DOCKER_USER%/symptom-tracker-web:latest
    docker push %DOCKER_USER%/symptom-tracker-web:v2.0.0-fastmcp
    
    echo.
    echo ========================================
    echo All images pushed successfully!
    echo ========================================
) else (
    echo.
    echo Images built but not pushed.
)

echo.
echo Images:
echo - %DOCKER_USER%/symptom-tracker-api:latest
echo - %DOCKER_USER%/symptom-tracker-api:v2.0.0-fastmcp
echo - %DOCKER_USER%/symptom-tracker-web:latest
echo - %DOCKER_USER%/symptom-tracker-web:v2.0.0-fastmcp
echo.
echo To run: docker-compose up -d
echo.
pause
