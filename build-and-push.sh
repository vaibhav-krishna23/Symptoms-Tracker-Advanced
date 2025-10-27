#!/bin/bash
# Build and Push Docker Images for FastMCP Version
# Version: 2.0.0-fastmcp

echo "========================================"
echo "Building Symptom Tracker Docker Images"
echo "Version: 2.0.0-fastmcp (FastMCP)"
echo "========================================"
echo ""

# Set your Docker Hub username
DOCKER_USER="vaibhavkrishna23"

# Build API image (with embedded FastMCP)
echo "[1/2] Building API image (FastAPI + FastMCP)..."
docker build -f Dockerfile.api -t $DOCKER_USER/symptom-tracker-api:latest -t $DOCKER_USER/symptom-tracker-api:v2.0.0-fastmcp .
if [ $? -ne 0 ]; then
    echo "ERROR: API build failed!"
    exit 1
fi
echo "✓ API image built successfully"
echo ""

# Build Web image
echo "[2/2] Building Web image (Streamlit)..."
docker build -f Dockerfile.web -t $DOCKER_USER/symptom-tracker-web:latest -t $DOCKER_USER/symptom-tracker-web:v2.0.0-fastmcp .
if [ $? -ne 0 ]; then
    echo "ERROR: Web build failed!"
    exit 1
fi
echo "✓ Web image built successfully"
echo ""

echo "========================================"
echo "All images built successfully!"
echo "========================================"
echo ""

# Ask to push
read -p "Push images to Docker Hub? (y/n): " PUSH
if [ "$PUSH" = "y" ] || [ "$PUSH" = "Y" ]; then
    echo ""
    echo "Pushing images to Docker Hub..."
    echo ""
    
    echo "Pushing API image..."
    docker push $DOCKER_USER/symptom-tracker-api:latest
    docker push $DOCKER_USER/symptom-tracker-api:v2.0.0-fastmcp
    
    echo "Pushing Web image..."
    docker push $DOCKER_USER/symptom-tracker-web:latest
    docker push $DOCKER_USER/symptom-tracker-web:v2.0.0-fastmcp
    
    echo ""
    echo "========================================"
    echo "All images pushed successfully!"
    echo "========================================"
else
    echo ""
    echo "Images built but not pushed."
fi

echo ""
echo "Images:"
echo "- $DOCKER_USER/symptom-tracker-api:latest"
echo "- $DOCKER_USER/symptom-tracker-api:v2.0.0-fastmcp"
echo "- $DOCKER_USER/symptom-tracker-web:latest"
echo "- $DOCKER_USER/symptom-tracker-web:v2.0.0-fastmcp"
echo ""
echo "To run: docker-compose up -d"
echo ""
