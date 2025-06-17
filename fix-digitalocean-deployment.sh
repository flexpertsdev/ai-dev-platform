#!/bin/bash

echo "🔧 Fixing DigitalOcean deployment..."
echo "This script will update your deployment to use the correct API URLs"

# Your droplet IP
DROPLET_IP="138.68.141.130"

# Create updated docker-compose.yml
cat > docker-compose.yml << EOF
version: '3.8'

services:
  app:
    build: 
      context: .
      args:
        - REACT_APP_API_BASE=http://${DROPLET_IP}:3001
        - REACT_APP_WS_BASE=ws://${DROPLET_IP}:8080
    ports:
      - "80:3000"
      - "3001:3001"
      - "8080:8080"
    environment:
      - NODE_ENV=production
      - REACT_APP_API_BASE=http://${DROPLET_IP}:3001
      - REACT_APP_WS_BASE=ws://${DROPLET_IP}:8080
    env_file:
      - .env
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ./workspaces:/workspaces
    privileged: true
    restart: unless-stopped
EOF

# Update Dockerfile to accept build args
cat > Dockerfile << 'EOF'
FROM node:18-bullseye

# Install Docker for DevContainer management
RUN apt-get update && apt-get install -y \
    docker.io \
    git \
    curl \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install DevPod CLI
RUN curl -L -o /usr/local/bin/devpod \
    "https://github.com/loft-sh/devpod/releases/latest/download/devpod-linux-amd64" \
    && chmod +x /usr/local/bin/devpod

# Install Claude Code CLI
RUN npm install -g @anthropic-ai/claude-code

# Create app directory
WORKDIR /app

# Copy all application code first
COPY backend/ ./backend/
COPY frontend/ ./frontend/
COPY ai-workspace-template/ ./ai-workspace-template/

# Install backend dependencies
WORKDIR /app/backend
RUN npm install

# Install frontend dependencies and build with env vars
WORKDIR /app/frontend
ARG REACT_APP_API_BASE
ARG REACT_APP_WS_BASE
RUN npm install && REACT_APP_API_BASE=$REACT_APP_API_BASE REACT_APP_WS_BASE=$REACT_APP_WS_BASE npm run build

WORKDIR /app

# Create workspace for user containers
RUN mkdir -p /workspace/containers

# Expose ports
EXPOSE 3000 3001 8080

# Start script
COPY start-poc.sh ./
RUN chmod +x start-poc.sh

CMD ["./start-poc.sh"]
EOF

echo "✅ Configuration files updated!"
echo ""
echo "Now run these commands on your DigitalOcean droplet:"
echo ""
echo "1. First, stop the current containers:"
echo "   docker-compose down"
echo ""
echo "2. Rebuild with the new configuration:"
echo "   docker-compose build --no-cache"
echo ""
echo "3. Start the updated platform:"
echo "   docker-compose up -d"
echo ""
echo "4. Check if it's running:"
echo "   docker-compose ps"
echo ""
echo "Your platform should then be accessible at:"
echo "http://${DROPLET_IP}"