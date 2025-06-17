# Fix DevPod Workspace Creation Error

The issue is that the server is trying to create GitHub repositories but either:
1. The template repository doesn't exist
2. The GitHub token doesn't have permissions
3. DevPod isn't properly configured

## Quick Fix - Use Simplified Server

Run these commands on your DigitalOcean droplet:

```bash
cd /root/ai-dev-platform

# 1. Copy the simplified server
docker-compose exec app cp /app/backend/server-simple.js /app/backend/server.js

# 2. Restart the backend
docker-compose restart

# 3. Check logs
docker-compose logs -f app
```

## Proper Fix - Set up GitHub Template

If you want the full GitHub integration:

### Step 1: Create Template Repository

1. Go to https://github.com/new
2. Repository name: `ai-workspace-template`
3. Make it public
4. Initialize with README
5. After creating, go to Settings → General → Template repository ✓

### Step 2: Upload Template Files

Push the template files from your local machine:

```bash
cd /Users/jos/Developer/ClaudePodv3/ai-workspace-template
git init
git remote add origin https://github.com/flexpertsdev/ai-workspace-template.git
git add .
git commit -m "Initial template"
git push -u origin main
```

### Step 3: Update Environment Variables

On the droplet:

```bash
cd /root/ai-dev-platform
nano .env

# Add/update:
GITHUB_TEMPLATE_OWNER=flexpertsdev
GITHUB_ORG=flexpertsdev
GITHUB_TOKEN=your_github_token_with_repo_permissions

# Restart
docker-compose restart
```

### Step 4: Test DevPod Setup

```bash
# Enter the container
docker-compose exec app bash

# Configure DevPod
devpod provider add docker
devpod provider use docker

# Test with a simple repo
devpod up https://github.com/devcontainers/templates.git --id test --provider docker
```

## Alternative: Skip DevPod for Testing

For quick testing without DevPod:

```bash
# Update the backend to use mock responses
docker-compose exec app sed -i 's/await devpod.createWorkspace/return {success: true, status: "mocked"}/g' /app/backend/server.js
docker-compose restart
```

The simplified server (server-simple.js) creates local workspaces without GitHub, which should work immediately.