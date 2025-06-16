FROM node:18-bullseye

# Install basic dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    python3 \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy all application code first
COPY backend/ ./backend/
COPY frontend/ ./frontend/
COPY ai-workspace-template/ ./ai-workspace-template/

# Install backend dependencies
WORKDIR /app/backend
RUN npm install

# Install frontend dependencies and build
WORKDIR /app/frontend
RUN npm install && npm run build

WORKDIR /app

# Create workspace for user containers
RUN mkdir -p /workspace/containers

# Expose ports
EXPOSE 3000 3001 8080

# Copy both start scripts
COPY start-railway.sh ./
COPY railway-server.js ./backend/
RUN chmod +x start-railway.sh

# Use Railway-specific start script
CMD ["./start-railway.sh"]