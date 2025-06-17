# Debug GitHub and DevPod Issues

The template repository exists and is properly configured. The issue is likely with the token permissions or DevPod setup.

## Run these commands on your DigitalOcean droplet:

### 1. Check GitHub Token Permissions

```bash
# Enter the container
docker-compose exec app bash

# Test GitHub token
curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user

# Test if token can create repos from template
curl -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  https://api.github.com/repos/flexpertsdev/ai-workspace-template/generate \
  -d '{"owner":"flexpertsdev","name":"test-workspace-manual","description":"Test workspace"}'
```

### 2. Debug DevPod Configuration

```bash
# Inside the container
docker-compose exec app bash

# Check DevPod providers
devpod provider list

# Add and configure Docker provider
devpod provider add docker || echo "Provider already exists"
devpod provider use docker

# Test DevPod with a simple public repo
devpod up https://github.com/microsoft/vscode-remote-try-node.git --id test-simple --provider docker
```

### 3. Check Docker-in-Docker

```bash
# Inside the container
docker-compose exec app bash

# Check if Docker daemon is running
docker ps

# If not running, start it
dockerd &
sleep 10

# Try again
docker ps
```

### 4. Manual Workspace Creation Test

```bash
# Inside the container
docker-compose exec app bash

# Create a test workspace manually
cd /workspaces
git clone https://github.com/flexpertsdev/ai-workspace-template.git test-manual
cd test-manual
devpod up . --id test-manual --provider docker
```

### 5. Check Environment Variables

```bash
# Check if env vars are set in container
docker-compose exec app env | grep -E "GITHUB|ANTHROPIC"
```

## Common Issues and Fixes:

### Issue: GitHub Token Insufficient Permissions
**Fix**: Create a new token with `repo` scope at https://github.com/settings/tokens

### Issue: Docker daemon not running in container
**Fix**: Update start script to ensure Docker starts:

```bash
# Edit start-poc.sh
docker-compose exec app nano /app/start-poc.sh

# Add at the beginning:
#!/bin/bash
# Start Docker daemon first
dockerd &
sleep 15
```

### Issue: DevPod provider not configured
**Fix**: Add provider configuration to startup:

```bash
# Update start-poc.sh to include:
devpod provider add docker || true
devpod provider use docker
```

## Quick Workaround - Skip DevPod

If DevPod continues to fail, update the backend to create simple Docker containers:

```bash
docker-compose exec app nano /app/backend/server.js

# Replace the DevPod creation with:
# Simple Docker container creation instead of DevPod
const command = `docker run -d --name ${workspaceId} -v ${workspacePath}:/workspace node:18 tail -f /dev/null`;
```

The real issue is likely that the GitHub token needs the `public_repo` and `repo` scopes to create repositories from templates.