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

# Install frontend dependencies and build
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