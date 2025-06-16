const express = require('express');
const path = require('path');
const cors = require('cors');
const WebSocket = require('ws');

const app = express();

// Middleware
app.use(cors());
app.use(express.json());

// Serve React frontend
app.use(express.static(path.join(__dirname, 'frontend/build')));

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'healthy', message: 'Chat interface is running!' });
});

// Simplified API endpoints for Railway
app.post('/api/workspaces/create', (req, res) => {
  res.json({
    success: true,
    workspaceId: `demo-${Date.now()}`,
    repositoryUrl: 'https://github.com/flexpertsdev/ai-workspace-template',
    message: 'Demo workspace created (DevContainers not available on Railway)',
    limited: true
  });
});

app.post('/api/workspaces/:workspaceId/chat', (req, res) => {
  const { message } = req.body;
  res.json({
    success: true,
    response: `I received your message: "${message}". Note: Full DevContainer functionality requires deployment to a VPS with Docker support. This is a demo mode.`,
    context_used: false,
    workspace_updated: false
  });
});

// Catch all - serve React app
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'frontend/build', 'index.html'));
});

// Start server on Railway's PORT
const PORT = process.env.PORT || 3001;
app.listen(PORT, () => {
  console.log(`🚀 Chat interface running on port ${PORT}`);
});

// WebSocket server (simplified)
const WS_PORT = process.env.WS_PORT || 8080;
const wss = new WebSocket.Server({ port: WS_PORT });

wss.on('connection', (ws) => {
  console.log('WebSocket client connected');
  
  ws.on('message', (data) => {
    const parsed = JSON.parse(data);
    
    // Simple echo response for demo
    ws.send(JSON.stringify({
      type: 'response',
      success: true,
      response: `Demo mode: "${parsed.message}". Deploy to VPS for full DevContainer support.`,
      timestamp: new Date().toISOString()
    }));
  });
});