# Final Fix for DevPod Issues

The workspace creation is working (GitHub repo is created) but DevPod is failing. Here are immediate fixes:

## Option 1: Quick Fix - Use Simple Containers (Recommended)

Run these commands on your DigitalOcean droplet:

```bash
cd /root/ai-dev-platform

# Create a patched server file
cat > backend/server-patched.js << 'EOF'
const express = require('express');
const cors = require('cors');
const { Octokit } = require('@octokit/rest');
const { exec } = require('child_process');
const { promisify } = require('util');
const WebSocket = require('ws');
const winston = require('winston');

const app = express();
const execAsync = promisify(exec);

// Logger setup
const logger = winston.createLogger({
  level: 'info',
  format: winston.format.json(),
  transports: [
    new winston.transports.Console({
      format: winston.format.simple()
    })
  ]
});

// GitHub API client
const octokit = new Octokit({
  auth: process.env.GITHUB_TOKEN
});

// Middleware
app.use(cors());
app.use(express.json());

// Simple container management (no DevPod)
class SimpleContainerManager {
  async createWorkspace(workspaceId, repoUrl) {
    try {
      logger.info(`Creating container workspace: ${workspaceId}`);
      
      // Clone the repository
      const workspacePath = `/workspaces/${workspaceId}`;
      await execAsync(`mkdir -p ${workspacePath}`);
      await execAsync(`git clone ${repoUrl} ${workspacePath}`);
      
      // Create a Docker container with the workspace mounted
      const containerCmd = `docker run -d \
        --name ${workspaceId} \
        -v ${workspacePath}:/workspace \
        -w /workspace \
        -e ANTHROPIC_API_KEY=${process.env.ANTHROPIC_API_KEY} \
        mcr.microsoft.com/devcontainers/typescript-node:18 \
        tail -f /dev/null`;
      
      await execAsync(containerCmd);
      
      // Install Claude Code in the container
      await execAsync(`docker exec ${workspaceId} npm install -g @anthropic-ai/claude-code`);
      
      return {
        success: true,
        workspaceId,
        status: 'created',
        output: 'Container created successfully'
      };
    } catch (error) {
      logger.error(`Failed to create workspace:`, error);
      return {
        success: false,
        error: error.message
      };
    }
  }
  
  async executeInWorkspace(workspaceId, message) {
    try {
      const escapedMessage = message.replace(/'/g, "'\\''");
      const command = `docker exec ${workspaceId} bash -c "cd /workspace && python3 .devcontainer/claude-handler.py '${escapedMessage}'"`;
      
      logger.info(`Executing in workspace ${workspaceId}`);
      const result = await execAsync(command, { maxBuffer: 1024 * 1024 * 10 });
      
      return JSON.parse(result.stdout);
    } catch (error) {
      logger.error(`Failed to execute in workspace:`, error);
      return {
        success: false,
        error: error.message,
        response: "I encountered an error processing your request."
      };
    }
  }
}

const containerManager = new SimpleContainerManager();

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// API Routes
app.post('/api/workspaces/create', async (req, res) => {
  try {
    const { userId, projectName, description } = req.body;
    
    if (!userId || !projectName) {
      return res.status(400).json({
        success: false,
        error: 'Missing required fields: userId and projectName'
      });
    }
    
    const workspaceId = `workspace-${userId}-${Date.now()}`;
    
    // 1. Create GitHub repository from template
    logger.info(`Creating GitHub repo for workspace: ${workspaceId}`);
    const repo = await octokit.repos.createUsingTemplate({
      template_owner: process.env.GITHUB_TEMPLATE_OWNER,
      template_repo: 'ai-workspace-template',
      owner: process.env.GITHUB_ORG,
      name: workspaceId,
      description: `AI Development Workspace: ${projectName}`,
      private: false
    });
    
    // Wait a bit for GitHub to process
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // 2. Create container workspace
    const workspace = await containerManager.createWorkspace(workspaceId, repo.data.clone_url);
    
    if (!workspace.success) {
      throw new Error(workspace.error);
    }
    
    res.json({
      success: true,
      workspaceId,
      repositoryUrl: repo.data.html_url,
      cloneUrl: repo.data.clone_url,
      workspace: workspace
    });
    
  } catch (error) {
    logger.error('Failed to create workspace:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

app.post('/api/workspaces/:workspaceId/chat', async (req, res) => {
  try {
    const { workspaceId } = req.params;
    const { message } = req.body;
    
    if (!message) {
      return res.status(400).json({
        success: false,
        error: 'Missing required field: message'
      });
    }
    
    const result = await containerManager.executeInWorkspace(workspaceId, message);
    res.json(result);
    
  } catch (error) {
    logger.error('Chat error:', error);
    res.status(500).json({
      success: false,
      error: error.message,
      response: "I encountered an error. Please try again."
    });
  }
});

// WebSocket server
const wss = new WebSocket.Server({ port: 8080 });

wss.on('connection', (ws) => {
  logger.info('WebSocket client connected');
  
  ws.on('message', async (data) => {
    try {
      const { type, workspaceId, message } = JSON.parse(data);
      
      if (type === 'chat') {
        ws.send(JSON.stringify({ type: 'typing', status: true }));
        
        const result = await containerManager.executeInWorkspace(workspaceId, message);
        
        ws.send(JSON.stringify({ 
          type: 'response', 
          ...result,
          timestamp: new Date().toISOString()
        }));
        
        ws.send(JSON.stringify({ type: 'typing', status: false }));
      }
    } catch (error) {
      ws.send(JSON.stringify({ 
        type: 'error', 
        error: error.message 
      }));
    }
  });
});

const PORT = process.env.PORT || 3001;
app.listen(PORT, () => {
  logger.info(`🚀 AI Dev Platform API (Simple Containers) running on port ${PORT}`);
  logger.info(`📡 WebSocket server running on port 8080`);
});
EOF

# Backup original and use patched version
docker-compose exec app cp /app/backend/server.js /app/backend/server-original.js
docker-compose exec app cp /app/backend/server-patched.js /app/backend/server.js

# Restart to apply changes
docker-compose restart

# Check logs
docker-compose logs -f
```

## Option 2: Fix DevPod (If you prefer)

```bash
# Enter container
docker-compose exec -it app bash

# Install DevPod manually
curl -L -o devpod https://github.com/loft-sh/devpod/releases/latest/download/devpod-linux-amd64
chmod +x devpod
mv devpod /usr/local/bin/

# Configure DevPod
export DOCKER_HOST=unix:///var/run/docker.sock
devpod provider add docker
devpod provider use docker

# Test with a simple repo
devpod up https://github.com/microsoft/vscode-remote-try-node.git --id test --provider docker
```

## Option 3: Debug Current Setup

```bash
# Check what's happening with DevPod
docker-compose exec app devpod list
docker-compose exec app devpod provider list
docker-compose exec app docker ps

# Check the actual error
docker-compose exec app devpod up https://github.com/flexpertsdev/workspace-demo-user-1750118537202.git --id test-debug --provider docker --debug
```

## Why This Happens

DevPod is failing because:
1. It's trying to use features that require a full Docker environment
2. The Docker-in-Docker setup might not have all required permissions
3. DevPod might be expecting a different container runtime

The simple container approach (Option 1) bypasses DevPod and creates containers directly, which is more reliable in this environment.