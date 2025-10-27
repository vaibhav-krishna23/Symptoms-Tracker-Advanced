#!/bin/bash

# Docker Hub username
DOCKER_USERNAME="vaibhavkrishna23"

# Image version
VERSION="latest"

echo "🐳 Building Docker images..."

# Build MCP Server
echo "Building MCP Server..."
docker build -f Dockerfile.mcp -t ${DOCKER_USERNAME}/symptom-tracker-mcp:${VERSION} .

# Build FastAPI
echo "Building FastAPI..."
docker build -f Dockerfile.api -t ${DOCKER_USERNAME}/symptom-tracker-api:${VERSION} .

# Build Streamlit
echo "Building Streamlit..."
docker build -f Dockerfile.web -t ${DOCKER_USERNAME}/symptom-tracker-web:${VERSION} .

echo "✅ All images built successfully!"

echo "🚀 Pushing images to Docker Hub..."

# Login to Docker Hub
echo "Please login to Docker Hub:"
docker login

# Push images
docker push ${DOCKER_USERNAME}/symptom-tracker-mcp:${VERSION}
docker push ${DOCKER_USERNAME}/symptom-tracker-api:${VERSION}
docker push ${DOCKER_USERNAME}/symptom-tracker-web:${VERSION}

echo "✅ All images pushed to Docker Hub!"
echo ""
echo "📦 Images available at:"
echo "   - ${DOCKER_USERNAME}/symptom-tracker-mcp:${VERSION}"
echo "   - ${DOCKER_USERNAME}/symptom-tracker-api:${VERSION}"
echo "   - ${DOCKER_USERNAME}/symptom-tracker-web:${VERSION}"
