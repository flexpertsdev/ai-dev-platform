# DigitalOcean Setup Instructions

## Create Droplet:

1. **Log in to DigitalOcean**
2. Click **"Create" → "Droplets"**
3. Configure:
   - **Choose an image**: Ubuntu 22.04 (LTS) x64
   - **Choose a plan**: Basic → Regular → $12/mo (2 GB / 1 CPU)
   - **Choose datacenter**: Select closest to you
   - **Authentication**: 
     - Password (easier) OR
     - SSH keys (more secure)
   - **Hostname**: `ai-dev-platform`
   - Click **"Create Droplet"**

## Once Created:

1. Note your Droplet's IP address (e.g., 164.92.xxx.xxx)
2. SSH into your droplet:
   ```bash
   ssh root@YOUR_DROPLET_IP
   ```

## Run the Deployment Script:

Once logged in via SSH, run these commands:

```bash
# Download and run the deployment script
curl -O https://raw.githubusercontent.com/flexpertsdev/ai-dev-platform/main/deploy-digitalocean.sh
chmod +x deploy-digitalocean.sh
./deploy-digitalocean.sh
```

## Configure API Keys:

After the script completes:

```bash
# Edit the .env file
nano .env

# Add your actual API keys:
ANTHROPIC_API_KEY=your_anthropic_api_key_here
GITHUB_TOKEN=your_github_token_here

# Save and exit (Ctrl+X, Y, Enter)
```

## Build and Deploy:

```bash
# Build the Docker containers
docker-compose build

# Start the platform
docker-compose up -d

# Check if it's running
docker-compose ps
```

## Access Your Platform:

Your platform will be available at:
http://YOUR_DROPLET_IP

## Optional: Set up a domain

1. Add an A record pointing to your droplet IP
2. Install nginx for SSL:
   ```bash
   apt install nginx certbot python3-certbot-nginx
   certbot --nginx -d yourdomain.com
   ```