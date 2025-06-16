import React, { useState, useEffect, useRef } from 'react';
import './App.css';

// Use window.location to dynamically determine API URLs
const API_BASE = process.env.REACT_APP_API_BASE || `http://${window.location.hostname}:3001`;
const WS_BASE = process.env.REACT_APP_WS_BASE || `ws://${window.location.hostname}:8080`;

interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
}

function App() {
  const [workspaceId, setWorkspaceId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [wsConnection, setWsConnection] = useState<WebSocket | null>(null);
  const [workspaceStatus, setWorkspaceStatus] = useState<'idle' | 'creating' | 'ready' | 'error'>('idle');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Initialize workspace and WebSocket connection
  useEffect(() => {
    initializeWorkspace();
  }, []);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const initializeWorkspace = async () => {
    try {
      setWorkspaceStatus('creating');
      
      const response = await fetch(`${API_BASE}/api/workspaces/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          userId: 'demo-user', // In real app, get from auth
          projectName: 'New React App',
          description: 'AI-generated React application'
        })
      });

      const data = await response.json();
      
      if (data.success) {
        setWorkspaceId(data.workspaceId);
        setWorkspaceStatus('ready');
        
        // Connect to WebSocket
        const ws = new WebSocket(WS_BASE);
        setWsConnection(ws);
        
        ws.onmessage = (event) => {
          const data = JSON.parse(event.data);
          handleWebSocketMessage(data);
        };
        
        // Welcome message
        addMessage('assistant', `🎉 Your development workspace is ready! 

I can help you build a React application through conversation. I have access to your complete workspace including:

📁 **Project files** - Your React app code  
📋 **Planning docs** - Requirements and specifications  
📂 **Reference materials** - Any files you want to upload  
💬 **Chat history** - Our previous conversations  

Your workspace: [${data.repositoryUrl}](${data.repositoryUrl})

What would you like to build?`);
        
      } else {
        throw new Error(data.error);
      }
    } catch (error: any) {
      setWorkspaceStatus('error');
      addMessage('system', `❌ Failed to create workspace: ${error.message}`);
    }
  };

  const handleWebSocketMessage = (data: any) => {
    switch (data.type) {
      case 'typing':
        setIsTyping(data.status);
        break;
      case 'response':
        setIsTyping(false);
        if (data.success) {
          addMessage('assistant', data.response);
        } else {
          addMessage('system', `❌ ${data.response}`);
        }
        break;
      case 'error':
        setIsTyping(false);
        addMessage('system', `❌ Error: ${data.error}`);
        break;
    }
  };

  const addMessage = (role: Message['role'], content: string) => {
    const message: Message = {
      id: Date.now() + Math.random() + '',
      role,
      content,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, message]);
  };

  const sendMessage = () => {
    if (!inputMessage.trim() || !wsConnection || workspaceStatus !== 'ready') return;

    // Add user message to UI
    addMessage('user', inputMessage);
    
    // Send to WebSocket
    wsConnection.send(JSON.stringify({
      type: 'chat',
      workspaceId,
      message: inputMessage
    }));

    setInputMessage('');
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const formatMessage = (content: string) => {
    // Simple markdown-like formatting
    return content
      .replace(/```(\w+)?\n([\s\S]*?)```/g, '<pre class="code-block"><code>$2</code></pre>')
      .replace(/`([^`]+)`/g, '<code class="inline-code">$1</code>')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');
  };

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <div className="header-content">
          <h1>🤖 AI Development Assistant</h1>
          <div className="workspace-status">
            <span className={`status-indicator ${workspaceStatus}`}></span>
            <span>Workspace: {workspaceStatus}</span>
          </div>
        </div>
      </header>

      {/* Chat Container */}
      <div className="chat-container">
        {/* Messages */}
        <div className="messages">
          {messages.map(message => (
            <div key={message.id} className={`message ${message.role}`}>
              <div className="message-bubble">
                <div 
                  className="message-content"
                  dangerouslySetInnerHTML={{ __html: formatMessage(message.content) }}
                />
                <div className="message-time">
                  {message.timestamp.toLocaleTimeString()}
                </div>
              </div>
            </div>
          ))}
          
          {/* Typing indicator */}
          {isTyping && (
            <div className="message assistant">
              <div className="message-bubble typing">
                <div className="typing-dots">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="input-area">
          <div className="input-container">
            <textarea
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Describe what you want to build..."
              disabled={workspaceStatus !== 'ready' || isTyping}
              className="message-input"
              rows={1}
            />
            <button
              onClick={sendMessage}
              disabled={!inputMessage.trim() || workspaceStatus !== 'ready' || isTyping}
              className="send-button"
            >
              {isTyping ? '⏳' : '📤'}
            </button>
          </div>
          
          {/* Quick suggestions */}
          <div className="quick-suggestions">
            <button onClick={() => setInputMessage("I want to build a todo list app with modern design")}>
              📝 Todo App
            </button>
            <button onClick={() => setInputMessage("Create a landing page for my business")}>
              🏢 Landing Page  
            </button>
            <button onClick={() => setInputMessage("Build a simple blog with React")}>
              📚 Blog
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
