#!/bin/bash
echo "Building and pushing all Docker images to vaibhav547/symptoms_tracker_advanced..."

echo ""
echo "========================================"
echo "Building MCP Server (SSE)"
echo "========================================"
docker build -f Dockerfile.mcp -t vaibhav547/symptoms_tracker_advanced:mcp-latest .
docker push vaibhav547/symptoms_tracker_advanced:mcp-latest

echo ""
echo "========================================"
echo "Building FastAPI Backend"
echo "========================================"
docker build -f Dockerfile.api -t vaibhav547/symptoms_tracker_advanced:api-latest .
docker push vaibhav547/symptoms_tracker_advanced:api-latest

echo ""
echo "========================================"
echo "Building Streamlit Frontend"
echo "========================================"
docker build -f Dockerfile.web -t vaibhav547/symptoms_tracker_advanced:web-latest .
docker push vaibhav547/symptoms_tracker_advanced:web-latest

echo ""
echo "========================================"
echo "All images built and pushed successfully!"
echo "========================================"
echo "MCP Server: vaibhav547/symptoms_tracker_advanced:mcp-latest"
echo "API Backend: vaibhav547/symptoms_tracker_advanced:api-latest"
echo "Web Frontend: vaibhav547/symptoms_tracker_advanced:web-latest"
echo ""
echo "Ready for Render deployment!"