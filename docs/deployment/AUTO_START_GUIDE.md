# AI-RSS-Hub Auto-Start on Boot Guide

> Keep your AI-RSS-Hub running even after server reboots

---

## 🎯 Overview

This guide will help you set up **AI-RSS-Hub** to automatically start when your server boots up using **systemd** service.

---

## 📋 Prerequisites

Check if you have everything needed:

```bash
# Check if systemd is available
systemctl --version

# Check Python
python3 --version

# Check if app is working
curl http://localhost:8000/api/health
```

---

## 🚀 Quick Setup (3 Steps)

### Step 1: Install the Service

Run the installation script with sudo:

```bash
cd /home/sam/Github/AI-RSS-Hub
sudo bash install_service.sh
```

This will:
- ✅ Stop any existing service
- ✅ Install the service file
- ✅ Enable auto-start on boot
- ✅ Start the service immediately

### Step 2: Verify Service is Running

```bash
sudo systemctl status ai-rss-hub
```

You should see:
```
● ai-rss-hub.service - AI-RSS-Hub - Intelligent RSS Aggregation System
     Loaded: loaded (/etc/systemd/system/ai-rss-hub.service; enabled)
     Active: active (running) since ...
```

### Step 3: Test the API

```bash
curl http://localhost:8000/api/health
```

Expected response:
```json
{
    "status": "ok",
    "message": "AI-RSS-Hub is running"
}
```

---

## 📊 Service Management

### Using systemd Commands

```bash
# Check service status
sudo systemctl status ai-rss-hub

# Start service
sudo systemctl start ai-rss-hub

# Stop service
sudo systemctl stop ai-rss-hub

# Restart service
sudo systemctl restart ai-rss-hub

# Enable auto-start on boot
sudo systemctl enable ai-rss-hub

# Disable auto-start on boot
sudo systemctl disable ai-rss-hub
```

### Using the Management Script (Easier)

```bash
cd /home/sam/Github/AI-RSS-Hub

# Interactive menu
./manage_service.sh

# Direct commands
./manage_service.sh status
./manage_service.sh start
./manage_service.sh stop
./manage_service.sh restart
./manage_service.sh test
```

---

## 📝 Viewing Logs

### View Live Logs (Follow Mode)

```bash
sudo journalctl -u ai-rss-hub -f
```

### View All Logs

```bash
sudo journalctl -u ai-rss-hub
```

### View Last 100 Lines

```bash
sudo journalctl -u ai-rss-hub -n 100
```

### View Logs Since Today

```bash
sudo journalctl -u ai-rss-hub --since today
```

### Using Management Script

```bash
./manage_service.sh logs      # Live logs
./manage_service.sh all-logs  # All logs
```

---

## 🔧 Service File Details

The service file is located at: `/etc/systemd/system/ai-rss-hub.service`

**Configuration:**
- **User**: `sam`
- **Working Directory**: `/home/sam/Github/AI-RSS-Hub`
- **Port**: `8000`
- **Host**: `0.0.0.0` (all interfaces)
- **Auto-restart**: Yes (after 10 seconds)
- **Auto-start on boot**: Yes (after installation)

---

## 🧪 Testing Auto-Start

To verify the service will start automatically on reboot:

### Option 1: Reboot the Server

```bash
sudo reboot
```

After reboot, check if service is running:
```bash
sudo systemctl status ai-rss-hub
curl http://localhost:8000/api/health
```

### Option 2: Simulate Boot (No Reboot)

```bash
# Stop the service
sudo systemctl stop ai-rss-hub

# Check if it's stopped
sudo systemctl status ai-rss-hub

# Start it (simulates boot start)
sudo systemctl start ai-rss-hub

# Check status
sudo systemctl status ai-rss-hub
```

---

## 🐛 Troubleshooting

### Issue 1: Service Failed to Start

**Check logs:**
```bash
sudo journalctl -u ai-rss-hub -n 50
```

**Common causes:**
- Virtual environment not found
- Python dependencies missing
- Port 8000 already in use
- .env file missing or misconfigured

**Solutions:**
```bash
# Check if port is in use
sudo lsof -i :8000

# Reinstall dependencies
source venv/bin/activate
pip install -r requirements.txt

# Check .env file
cat .env
```

### Issue 2: Service Starts But API Not Responding

**Test API:**
```bash
curl http://localhost:8000/api/health
curl http://8.134.202.27:8000/api/health
```

**Check firewall:**
```bash
sudo ufw status
sudo ufw allow 8000/tcp
```

**Check if service is listening:**
```bash
sudo netstat -tlnp | grep 8000
# or
sudo ss -tlnp | grep 8000
```

### Issue 3: Service Keeps Restarting

**Check logs for errors:**
```bash
sudo journalctl -u ai-rss-hub -n 100
```

**Possible causes:**
- Database corruption
- Missing API keys
- Import errors

**Fix:**
```bash
# Test manually first
cd /home/sam/Github/AI-RSS-Hub
source venv/bin/activate
python -m app.main

# If manual start works, check service logs
```

### Issue 4: Permission Denied

**Ensure correct permissions:**
```bash
sudo chown -R sam:sam /home/sam/Github/AI-RSS-Hub
chmod +x /home/sam/Github/AI-RSS-Hub/*.sh
```

---

## 📊 Monitoring

### Check Service Health

Create a simple monitoring script:

```bash
#!/bin/bash
# monitor.sh - Check if AI-RSS-Hub is running

if curl -s http://localhost:8000/api/health > /dev/null; then
    echo "✅ AI-RSS-Hub is running"
    exit 0
else
    echo "❌ AI-RSS-Hub is down"
    sudo systemctl restart ai-rss-hub
    exit 1
fi
```

### Add to Crontab for Auto-Recovery

```bash
# Edit crontab
crontab -e

# Add this line to check every 5 minutes
*/5 * * * * /home/sam/Github/AI-RSS-Hub/monitor.sh
```

---

## 🔄 Updating the Service

If you update the application code:

```bash
# 1. Pull or update your code
cd /home/sam/Github/AI-RSS-Hub
git pull  # or however you update

# 2. Restart the service
sudo systemctl restart ai-rss-hub

# 3. Verify it's working
curl http://localhost:8000/api/health
```

---

## 📁 File Locations

| File | Location | Purpose |
|------|----------|---------|
| Service File | `/etc/systemd/system/ai-rss-hub.service` | Systemd configuration |
| App Directory | `/home/sam/Github/AI-RSS-Hub` | Application files |
| Logs | `journalctl -u ai-rss-hub` | Service logs |
| Database | `/home/sam/Github/AI-RSS-Hub/ai_rss_hub.db` | SQLite database |

---

## 🔐 Security Considerations

The service file includes these security settings:

```ini
NoNewPrivileges=true    # Prevent privilege escalation
PrivateTmp=true         # Use private /tmp directory
```

For production, consider:
- Running as dedicated user (not sam)
- Setting up firewall rules
- Using HTTPS/SSL
- Regular security updates

---

## 📞 Quick Reference

### Essential Commands

```bash
# Install service
sudo bash install_service.sh

# Check status
sudo systemctl status ai-rss-hub

# Restart service
sudo systemctl restart ai-rss-hub

# View logs
sudo journalctl -u ai-rss-hub -f

# Test API
curl http://localhost:8000/api/health
```

### Using Management Script

```bash
./manage_service.sh          # Interactive menu
./manage_service.sh status   # Quick status check
./manage_service.sh test     # Test API
```

---

## ✅ Verification Checklist

After installation, verify:

- [ ] Service is enabled: `systemctl is-enabled ai-rss-hub`
- [ ] Service is running: `systemctl is-active ai-rss-hub`
- [ ] API responds: `curl http://localhost:8000/api/health`
- [ ] Auto-start on boot: `systemctl is-enabled ai-rss-hub`
- [ ] Logs are accessible: `journalctl -u ai-rss-hub`

---

## 🎉 Success!

Your AI-RSS-Hub will now:
- ✅ Start automatically on boot
- ✅ Restart automatically if it crashes
- ✅ Run in the background
- ✅ Log all activity to system journal

---

## 📚 Additional Resources

- **Systemd Documentation**: https://www.freedesktop.org/software/systemd/man/systemd.service.html
- **Client Usage Guide**: `CLIENT_USAGE_GUIDE.md`
- **Postman Guide**: `POSTMAN_GUIDE.md`

---

**Last Updated:** 2026-01-03
**Server:** http://8.134.202.27:8000
