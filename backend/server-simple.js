const express = require('express');
const cors = require('cors');
const { exec } = require('child_process');
const { promisify } = require('util');
const WebSocket = require('ws');
const fs = require('fs').promises;
const path = require('path');

const app = express();
const execAsync = promisify(exec);

// Middleware
app.use(cors());
app.use(express.json());

// Simple DevPod Manager without GitHub
class SimpleDevPodManager {
  constructor() {
    this.workspacesDir = '/workspaces';
  }

  async createWorkspace(workspaceId, projectName) {
    try {
      console.log(`Creating local workspace: ${workspaceId}`);
      
      // Create local workspace directory
      const workspacePath = path.join(this.workspacesDir, workspaceId);
      await fs.mkdir(workspacePath, { recursive: true });
      
      // Copy template files
      const templatePath = '/app/ai-workspace-template';
      const copyCommand = `cp -r ${templatePath}/* ${workspacePath}/`;
      await execAsync(copyCommand);
      
      // Initialize git repo
      await execAsync(`cd ${workspacePath} && git init`);
      
      // Create DevPod workspace from local path
      const command = `devpod up ${workspacePath} --id ${workspaceId} --provider docker`;
      console.log(`Running: ${command}`);
      const result = await execAsync(command, { timeout: 300000 }); // 5 min timeout
      
      return {
        success: true,
        workspaceId,
        status: 'created',
        output: result.stdout
      };
    } catch (error) {
      console.error(`Failed to create workspace:`, error);
      return {
        success: false,
        error: error.message
      };
    }
  }
  
  async executeInWorkspace(workspaceId, message) {
    try {
      const escapedMessage = message.replace(/'/g, "'\\''");
      const command = `devpod ssh ${workspaceId} --command "cd /workspace && python3 .devcontainer/claude-handler.py '${escapedMessage}'"`;
      
      console.log(`Executing in workspace ${workspaceId}`);
      const result = await execAsync(command, { maxBuffer: 1024 * 1024 * 10 });
      
      return JSON.parse(result.stdout);
    } catch (error) {
      console.error(`Failed to execute in workspace:`, error);
      return {
        success: false,
        error: error.message,
        response: "I encountered an error processing your request."
      };
    }
  }
}

const devpod = new SimpleDevPodManager();

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
    
    // Create local workspace (no GitHub)
    const workspace = await devpod.createWorkspace(workspaceId, projectName);
    
    if (!workspace.success) {
      throw new Error(workspace.error);
    }
    
    res.json({
      success: true,
      workspaceId,
      workspace: workspace,
      repositoryUrl: 'local',
      cloneUrl: 'local'
    });
    
  } catch (error) {
    console.error('Failed to create workspace:', error);
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
    
    const result = await devpod.executeInWorkspace(workspaceId, message);
    res.json(result);
    
  } catch (error) {
    console.error('Chat error:', error);
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
  console.log('WebSocket client connected');
  
  ws.on('message', async (data) => {
    try {
      const { type, workspaceId, message } = JSON.parse(data);
      
      if (type === 'chat') {
        ws.send(JSON.stringify({ type: 'typing', status: true }));
        
        const result = await devpod.executeInWorkspace(workspaceId, message);
        
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
  console.log(`🚀 Simple AI Dev Platform API running on port ${PORT}`);
  console.log(`📡 WebSocket server running on port 8080`);
});