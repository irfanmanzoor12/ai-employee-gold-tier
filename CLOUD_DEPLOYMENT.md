# Cloud Deployment Guide - Platinum Tier

Deploy your AI Employee on Oracle Cloud Free Tier for 24/7 operation.

## Oracle Cloud Free Tier (Always Free)

**What you get FREE forever:**
- 2 AMD VMs (1 GB RAM each) or 1 ARM VM (4 cores, 24 GB RAM)
- 200 GB block storage
- 10 TB/month outbound data

## Step 1: Create Oracle Cloud Account

1. Go to: https://www.oracle.com/cloud/free/
2. Click "Start for free"
3. Use real info (they verify identity)
4. Credit card required but **NOT charged** for free tier

## Step 2: Create Free VM

1. Go to Oracle Cloud Console
2. Click "Create a VM instance"
3. Choose:
   - **Shape**: VM.Standard.E2.1.Micro (always free)
   - **Image**: Ubuntu 22.04 (recommended)
   - **SSH Key**: Generate or upload your key

4. Click "Create"
5. Note the **Public IP** when ready

## Step 3: Connect to VM

```bash
# From your local machine
ssh -i ~/.ssh/your-key ubuntu@<PUBLIC_IP>
```

## Step 4: Setup VM Environment

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.13+ and dependencies
sudo apt install -y python3 python3-pip python3-venv git

# Install uv (fast Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc

# Install Node.js (for MCP servers if needed)
curl -fsSL https://deb.nodesource.com/setup_24.x | sudo -E bash -
sudo apt install -y nodejs

# Install PM2 (process manager for 24/7)
sudo npm install -g pm2
```

## Step 5: Clone Your Project

```bash
# Clone watchers code
git clone <your-watchers-repo> ~/watchers
cd ~/watchers

# Setup Python environment
uv venv
uv sync

# Clone vault (will sync with local)
git clone <your-vault-repo> ~/AI_Employee_Vault
```

## Step 6: Configure Environment

```bash
# Create .env file (secrets stay on cloud, not in git)
nano ~/watchers/.env
```

Add:
```
OPENAI_API_KEY=your-key
# Odoo credentials when ready
```

## Step 7: Start Services with PM2

```bash
cd ~/watchers

# Start Gmail watcher
pm2 start "uv run python gmail_watcher.py" --name gmail-watcher

# Start File watcher
pm2 start "uv run python file_watcher.py" --name file-watcher

# Start Frontend (optional - expose via nginx)
pm2 start "uv run streamlit run frontend_app.py --server.port 8501" --name frontend

# Start Scheduler
pm2 start "uv run python scheduler.py" --name scheduler

# Save PM2 config to survive reboots
pm2 save
pm2 startup
```

## Step 8: Setup Vault Sync (Cloud <-> Local)

### On Cloud VM:
```bash
cd ~/AI_Employee_Vault

# Setup auto-pull every 5 minutes
crontab -e
# Add: */5 * * * * cd ~/AI_Employee_Vault && git pull origin main
```

### On Local Machine:
```bash
cd /mnt/d/Irfan/FTE-H/AI_Employee_Vault

# Push changes
git push origin main

# Or setup auto-push
# Watch for changes and push
```

## Step 9: Expose Frontend (Optional)

```bash
# Install nginx
sudo apt install -y nginx

# Configure reverse proxy
sudo nano /etc/nginx/sites-available/ai-employee
```

Add:
```nginx
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/ai-employee /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

Access at: `http://<PUBLIC_IP>`

## Step 10: Health Monitoring

```bash
# Check all processes
pm2 status

# View logs
pm2 logs

# Monitor resources
pm2 monit
```

## Work-Zone Split (Platinum Requirement)

| Component | Runs On | Responsibility |
|-----------|---------|----------------|
| Gmail Watcher | Cloud | Triage + draft replies |
| File Watcher | Cloud | Monitor Needs_Action |
| Scheduler | Cloud | Run weekly audits |
| Frontend | Cloud | View dashboard |
| Approval Actions | Local | Approve/reject sensitive actions |
| Payments/Banking | Local | Execute financial actions |
| WhatsApp Session | Local | Personal messaging |

## Security Checklist

- [ ] .env files NEVER in git
- [ ] Vault sync excludes credentials
- [ ] SSH key authentication only (no passwords)
- [ ] Firewall: only ports 22, 80, 443 open
- [ ] Sensitive actions require Local approval

## Quick Commands

```bash
# Check status
pm2 status

# Restart all
pm2 restart all

# View logs
pm2 logs gmail-watcher

# Stop everything
pm2 stop all
```

## Troubleshooting

**VM runs out of memory:**
```bash
# Add swap
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

**Process keeps crashing:**
```bash
# Check logs
pm2 logs <name> --lines 100

# Increase restart delay
pm2 delete <name>
pm2 start <command> --name <name> --restart-delay=5000
```

---

## Demo Flow (Platinum Gate)

1. Email arrives (while you're offline)
2. Cloud Gmail Watcher detects it
3. Cloud creates draft reply in `/Pending_Approval/`
4. Vault syncs to Local (git pull)
5. You review and move to `/Approved/`
6. Vault syncs to Cloud (git push)
7. Cloud detects approval, sends email via MCP
8. Moves task to `/Done/`
9. Logged in `/Logs/`

This proves your AI Employee works 24/7 autonomously with human-in-the-loop.
