#!/bin/bash

echo "🚀 Starting AI Dev Platform with DevPod fix..."

# Start Docker daemon (for DevContainers)
echo "Starting Docker daemon..."
dockerd &

# Wait for Docker to be ready
echo "Waiting for Docker to initialize..."
sleep 20

# Verify Docker is running
until docker ps > /dev/null 2>&1; do
    echo "Waiting for Docker daemon..."
    sleep 5
done
echo "✅ Docker is ready"

# Configure DevPod
echo "Configuring DevPod..."
devpod provider add docker --option DOCKER_HOST=unix:///var/run/docker.sock || echo "Provider exists"
devpod provider use docker
echo "✅ DevPod configured"

# Create workspaces directory
mkdir -p /workspaces

# Start backend API
echo "Starting backend API..."
cd /app/backend && npm start &

# Serve frontend (static files)
echo "Starting frontend..."
cd /app/frontend/build && python3 -m http.server 3000 &

echo "✅ All services started"
echo "📡 API running on port 3001"
echo "🌐 Frontend running on port 3000"
echo "🔌 WebSocket running on port 8080"

# Keep container running
wait