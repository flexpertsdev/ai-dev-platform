const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');
const { Octokit } = require('@octokit/rest');
const { exec } = require('child_process');
const { promisify } = require('util');
const WebSocket = require('ws');
const cors = require('cors');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const winston = require('winston');
require('dotenv').config();

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

// Middleware
app.use(helmet());
app.use(cors());
app.use(express.json());

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100 // limit each IP to 100 requests per windowMs
});

const createLimiter = rateLimit({
  windowMs: 60 * 60 * 1000, // 1 hour
  max: 5 // limit each IP to 5 workspace creations per hour
});

app.use('/api/', limiter);
app.use('/api/workspaces/create', createLimiter);

// GitHub API client
const octokit = new Octokit({
  auth: process.env.GITHUB_TOKEN
});

// DevPod workspace management
class DevPodManager {
  async createWorkspace(workspaceId, repoUrl) {
    try {
      const command = `devpod up ${repoUrl} --id ${workspaceId} --provider docker`;
      logger.info(`Creating workspace: ${workspaceId}`);
      const result = await execAsync(command);
      
      return {
        success: true,
        workspaceId,
        status: 'created',
        output: result.stdout
      };
    } catch (error) {
      logger.error(`Failed to create workspace ${workspaceId}:`, error);
      return {
        success: false,
        error: error.message
      };
    }
  }
  
  async executeInWorkspace(workspaceId, message) {
    try {
      // Escape single quotes in the message
      const escapedMessage = message.replace(/'/g, "'\\''");
      const command = `devpod ssh ${workspaceId} --command "cd /workspace && python3 .devcontainer/claude-handler.py '${escapedMessage}'"`;
      
      logger.info(`Executing in workspace ${workspaceId}`);
      const result = await execAsync(command, { maxBuffer: 1024 * 1024 * 10 });
      
      return JSON.parse(result.stdout);
    } catch (error) {
      logger.error(`Failed to execute in workspace ${workspaceId}:`, error);
      return {
        success: false,
        error: error.message,
        response: "I encountered an error processing your request."
      };
    }
  }
  
  async getWorkspaceStatus(workspaceId) {
    try {
      const command = `devpod list --output json`;
      const result = await execAsync(command);
      const workspaces = JSON.parse(result.stdout);
      
      const workspace = workspaces.find(w => w.id === workspaceId);
      return workspace || { status: 'not_found' };
    } catch (error) {
      logger.error(`Failed to get workspace status ${workspaceId}:`, error);
      return { status: 'error', error: error.message };
    }
  }
  
  async stopWorkspace(workspaceId) {
    try {
      const command = `devpod stop ${workspaceId}`;
      await execAsync(command);
      logger.info(`Stopped workspace: ${workspaceId}`);
      return { success: true };
    } catch (error) {
      logger.error(`Failed to stop workspace ${workspaceId}:`, error);
      return { success: false, error: error.message };
    }
  }
  
  async deleteWorkspace(workspaceId) {
    try {
      const command = `devpod delete ${workspaceId} --force`;
      await execAsync(command);
      logger.info(`Deleted workspace: ${workspaceId}`);
      return { success: true };
    } catch (error) {
      logger.error(`Failed to delete workspace ${workspaceId}:`, error);
      return { success: false, error: error.message };
    }
  }
}

const devpod = new DevPodManager();

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'healthy', timestamp: new Date().toISOString() });
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
    
    // 2. Create DevPod workspace
    const workspace = await devpod.createWorkspace(workspaceId, repo.data.clone_url);
    
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
    
    // Execute Claude Code in workspace
    const result = await devpod.executeInWorkspace(workspaceId, message);
    
    res.json(result);
    
  } catch (error) {
    logger.error('Failed to process chat:', error);
    res.status(500).json({
      success: false,
      error: error.message,
      response: "I encountered an error. Please try again."
    });
  }
});

app.get('/api/workspaces/:workspaceId/status', async (req, res) => {
  try {
    const { workspaceId } = req.params;
    const status = await devpod.getWorkspaceStatus(workspaceId);
    
    res.json(status);
    
  } catch (error) {
    logger.error('Failed to get workspace status:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

app.post('/api/workspaces/:workspaceId/stop', async (req, res) => {
  try {
    const { workspaceId } = req.params;
    const result = await devpod.stopWorkspace(workspaceId);
    
    res.json(result);
    
  } catch (error) {
    logger.error('Failed to stop workspace:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

app.delete('/api/workspaces/:workspaceId', async (req, res) => {
  try {
    const { workspaceId } = req.params;
    const result = await devpod.deleteWorkspace(workspaceId);
    
    res.json(result);
    
  } catch (error) {
    logger.error('Failed to delete workspace:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// WebSocket for real-time updates
const wss = new WebSocket.Server({ port: process.env.WS_PORT || 8080 });

wss.on('connection', (ws) => {
  logger.info('New WebSocket connection');
  
  ws.on('message', async (data) => {
    try {
      const { type, workspaceId, message } = JSON.parse(data);
      
      if (type === 'chat') {
        // Send typing indicator
        ws.send(JSON.stringify({ type: 'typing', status: true }));
        
        // Process with Claude Code
        const result = await devpod.executeInWorkspace(workspaceId, message);
        
        // Send response
        ws.send(JSON.stringify({ 
          type: 'response', 
          ...result,
          timestamp: new Date().toISOString()
        }));
        
        // Stop typing indicator
        ws.send(JSON.stringify({ type: 'typing', status: false }));
      }
    } catch (error) {
      logger.error('WebSocket error:', error);
      ws.send(JSON.stringify({ 
        type: 'error', 
        error: error.message 
      }));
    }
  });
  
  ws.on('close', () => {
    logger.info('WebSocket connection closed');
  });
});

const PORT = process.env.PORT || 3001;
app.listen(PORT, () => {
  logger.info(`🚀 AI Development Platform API running on port ${PORT}`);
  logger.info(`📡 WebSocket server running on port ${process.env.WS_PORT || 8080}`);
});