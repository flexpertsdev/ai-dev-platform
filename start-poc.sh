#!/bin/bash

echo "🚀 Starting AI Dev Platform POC..."

# Start Docker daemon (for DevContainers)
dockerd &

# Wait for Docker to be ready
sleep 10

# Configure DevPod for Railway environment
devpod provider add docker || true
devpod provider use docker

# Start backend API
cd backend && npm start &

# Serve frontend (static files)
cd ../frontend/build && python3 -m http.server 3000 &

# Keep container running
wait