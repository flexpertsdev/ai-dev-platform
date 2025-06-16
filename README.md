# AI Development Platform with Claude Code

A SaaS platform that creates complete development workspaces where Claude Code operates with full context to help non-technical users build React applications through natural conversation.

## 🚀 Overview

This platform provides each user with their own GitHub repository workspace integrated with DevContainers, where Claude Code has access to not just project code, but planning documents, reference materials, chat history, and assets.

### Key Features

- **Full Context AI Development**: Claude Code operates inside DevContainers with complete workspace context
- **GitHub Integration**: Each user gets their own GitHub repository workspace
- **Real-time Chat Interface**: WebSocket-powered chat for instant AI responses
- **Auto-sync**: All changes automatically saved to GitHub
- **Persistent Chat History**: No lost context between sessions
- **React Development Ready**: Pre-configured with React, TypeScript, and modern tools

## 🏗️ Architecture

```
[Chat UI] ↔ [Backend API] ↔ [DevPod Manager] ↔ [DevContainer + Claude Code] ↔ [GitHub Workspace Repo]
```

## 📁 Project Structure

```
ClaudePodv3/
├── backend/                    # Express API server
│   ├── server.js              # Main API server with DevPod management
│   ├── package.json
│   └── .env.example
├── frontend/                   # React chat interface
│   ├── src/
│   │   ├── App.tsx           # Main chat component
│   │   └── App.css           # Styling
│   ├── package.json
│   └── .env.example
├── ai-workspace-template/      # GitHub template repository
│   ├── .devcontainer/         # DevContainer configuration
│   │   ├── devcontainer.json
│   │   ├── Dockerfile
│   │   ├── setup.sh
│   │   ├── auto-sync.sh
│   │   └── claude-handler.py
│   ├── project/               # User's React app
│   ├── planning/              # Planning documents
│   ├── reference/             # Reference materials
│   ├── chat-history/          # Chat logs
│   └── iterations/            # Version history
├── Dockerfile                  # POC deployment container
├── railway.toml               # Railway configuration
└── start-poc.sh              # POC startup script
```

## 🚀 Quick Start

### Prerequisites

- Node.js 18+
- Docker
- GitHub account with personal access token
- Anthropic API key
- DevPod CLI installed

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/ClaudePodv3.git
   cd ClaudePodv3
   ```

2. **Set up environment variables**
   ```bash
   # Backend
   cd backend
   cp .env.example .env
   # Edit .env with your credentials
   
   # Frontend
   cd ../frontend
   cp .env.example .env
   ```

3. **Install dependencies**
   ```bash
   # Backend
   cd backend
   npm install
   
   # Frontend
   cd ../frontend
   npm install
   ```

4. **Create GitHub template repository**
   - Create a new GitHub repository named `ai-workspace-template`
   - Copy contents of `ai-workspace-template/` directory to the repository
   - Enable template repository in settings

5. **Start the platform**
   ```bash
   # Terminal 1: Start backend
   cd backend
   npm start
   
   # Terminal 2: Start frontend
   cd frontend
   npm start
   ```

6. **Access the platform**
   - Open http://localhost:3000
   - The chat interface will create a workspace and connect to Claude Code

## 🚢 Deployment

### POC Deployment (Railway)

1. **Install Railway CLI**
   ```bash
   npm install -g @railway/cli
   railway login
   ```

2. **Create new Railway project**
   ```bash
   railway new
   ```

3. **Set environment variables**
   ```bash
   railway variables set ANTHROPIC_API_KEY=your_key
   railway variables set GITHUB_TOKEN=your_token
   railway variables set GITHUB_TEMPLATE_OWNER=your_username
   railway variables set GITHUB_ORG=your_org
   ```

4. **Deploy**
   ```bash
   railway up
   ```

### Production Deployment

See `CLAUDE.md` for detailed production deployment instructions with separated architecture (Netlify + Railway + DigitalOcean).

## 🔧 Configuration

### Environment Variables

**Backend (.env)**
```bash
ANTHROPIC_API_KEY=sk-ant-...
GITHUB_TOKEN=ghp_...
GITHUB_TEMPLATE_OWNER=yourusername
GITHUB_ORG=yourorg
PORT=3001
WS_PORT=8080
```

**Frontend (.env)**
```bash
REACT_APP_API_BASE=http://localhost:3001
REACT_APP_WS_BASE=ws://localhost:8080
```

## 🤖 How It Works

1. **User opens chat interface** → Creates a new GitHub workspace repository
2. **DevPod creates container** → Launches DevContainer with Claude Code
3. **User describes project** → Claude Code builds React app iteratively
4. **Auto-sync to GitHub** → All changes saved automatically
5. **Full context maintained** → Chat history, planning docs, and code all accessible

## 📚 Workspace Structure

Each user workspace includes:

- `project/` - The React application being built
- `planning/` - Requirements and specifications
- `reference/` - User-uploaded examples and inspiration
- `chat-history/` - Conversation logs
- `iterations/` - Version history
- `assets/` - Images and brand materials

## 🔒 Security Considerations

- Rate limiting on API endpoints
- Workspace resource limits (CPU, memory, storage)
- Isolated containers per workspace
- Secure environment variable management
- Automatic cleanup of inactive workspaces

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with Claude Code integration
- Powered by DevContainers and DevPod
- GitHub API for repository management
- Railway for easy deployment