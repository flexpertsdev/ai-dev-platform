#!/bin/bash

# DigitalOcean Deployment Script for AI Dev Platform
# Run this on your DigitalOcean Droplet after SSH-ing in

echo "🚀 AI Dev Platform - DigitalOcean Deployment Script"
echo "=================================================="

# Update system
echo "📦 Updating system packages..."
sudo apt-get update
sudo apt-get upgrade -y

# Install Docker
echo "🐋 Installing Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
echo "🐋 Installing Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Node.js
echo "📦 Installing Node.js..."
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install DevPod
echo "🔧 Installing DevPod..."
curl -L -o devpod "https://github.com/loft-sh/devpod/releases/latest/download/devpod-linux-amd64"
sudo install -c -m 0755 devpod /usr/local/bin/devpod
rm devpod

# Clone the repository
echo "📥 Cloning AI Dev Platform..."
git clone https://github.com/flexpertsdev/ai-dev-platform.git
cd ai-dev-platform

# Create .env file
echo "🔐 Creating environment configuration..."
cat > .env << 'EOF'
ANTHROPIC_API_KEY=<YOUR_ANTHROPIC_API_KEY>
GITHUB_TOKEN=<YOUR_GITHUB_TOKEN>
GITHUB_TEMPLATE_OWNER=flexpertsdev
GITHUB_ORG=flexpertsdev
PORT=3001
WS_PORT=8080
NODE_ENV=production
DEVPOD_PROVIDER=docker
EOF

echo "⚠️  IMPORTANT: Edit .env file with your actual API keys!"
echo ""

# Create systemd service
echo "🔧 Creating systemd service..."
sudo tee /etc/systemd/system/ai-dev-platform.service > /dev/null << 'EOF'
[Unit]
Description=AI Development Platform
After=docker.service
Requires=docker.service

[Service]
Type=simple
Restart=always
RestartSec=5
WorkingDirectory=/root/ai-dev-platform
ExecStart=/usr/bin/docker-compose up
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Create docker-compose.yml
echo "🐋 Creating Docker Compose configuration..."
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  app:
    build: .
    ports:
      - "80:3000"
      - "3001:3001"
      - "8080:8080"
    environment:
      - NODE_ENV=production
    env_file:
      - .env
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ./workspaces:/workspaces
    privileged: true
    restart: unless-stopped
EOF

# Create production Dockerfile
echo "📝 Creating production Dockerfile..."
cat > Dockerfile << 'EOF'
FROM node:18-bullseye

# Install Docker & DevPod
RUN apt-get update && apt-get install -y \
    docker.io \
    git \
    curl \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install DevPod
RUN curl -L -o /usr/local/bin/devpod \
    "https://github.com/loft-sh/devpod/releases/latest/download/devpod-linux-amd64" \
    && chmod +x /usr/local/bin/devpod

# Install Claude Code CLI
RUN npm install -g @anthropic-ai/claude-code

# Copy application
WORKDIR /app
COPY . .

# Install dependencies
WORKDIR /app/backend
RUN npm install

WORKDIR /app/frontend
RUN npm install && npm run build

WORKDIR /app

# Start script
RUN echo '#!/bin/bash\n\
# Start Docker daemon\n\
dockerd &\n\
sleep 10\n\
# Configure DevPod\n\
devpod provider add docker || true\n\
devpod provider use docker\n\
# Start backend\n\
cd /app/backend && npm start &\n\
# Serve frontend\n\
cd /app && npx serve -s frontend/build -l 3000 &\n\
wait' > start.sh && chmod +x start.sh

EXPOSE 3000 3001 8080

CMD ["./start.sh"]
EOF

echo "✅ Deployment script ready!"
echo ""
echo "Next steps:"
echo "1. Edit the .env file with your API keys:"
echo "   nano .env"
echo ""
echo "2. Build and start the platform:"
echo "   docker-compose build"
echo "   docker-compose up -d"
echo ""
echo "3. Enable auto-start on boot:"
echo "   sudo systemctl enable ai-dev-platform"
echo "   sudo systemctl start ai-dev-platform"
echo ""
echo "4. Your platform will be available at:"
echo "   http://YOUR_DROPLET_IP"
echo ""
echo "5. (Optional) Set up a domain and SSL with Nginx"
echo ""
echo "🎉 Ready to build and deploy!"