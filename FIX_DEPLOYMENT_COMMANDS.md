# Fix DigitalOcean Deployment - CORS/Connection Issues

Run these commands on your DigitalOcean droplet (138.68.141.130):

```bash
# 1. Navigate to the app directory
cd /root/ai-dev-platform

# 2. Stop current containers
docker-compose down

# 3. Update docker-compose.yml with correct IPs
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  app:
    build: 
      context: .
      args:
        - REACT_APP_API_BASE=http://138.68.141.130:3001
        - REACT_APP_WS_BASE=ws://138.68.141.130:8080
    ports:
      - "80:3000"
      - "3001:3001"
      - "8080:8080"
    environment:
      - NODE_ENV=production
      - REACT_APP_API_BASE=http://138.68.141.130:3001
      - REACT_APP_WS_BASE=ws://138.68.141.130:8080
    env_file:
      - .env
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ./workspaces:/workspaces
    privileged: true
    restart: unless-stopped
EOF

# 4. Update the Dockerfile to handle build args
sed -i 's/RUN npm install && npm run build/ARG REACT_APP_API_BASE\nARG REACT_APP_WS_BASE\nRUN npm install \&\& REACT_APP_API_BASE=$REACT_APP_API_BASE REACT_APP_WS_BASE=$REACT_APP_WS_BASE npm run build/g' Dockerfile

# 5. Rebuild the containers with new configuration
docker-compose build --no-cache

# 6. Start the platform
docker-compose up -d

# 7. Check logs
docker-compose logs -f
```

After running these commands, your platform should be accessible at:
http://138.68.141.130

The frontend will now correctly connect to the backend API at the droplet's IP address instead of localhost.