# Reboot Test Instructions

> Test if AI-RSS-Hub auto-starts on boot

---

## 🔄 Step-by-Step Process

### Step 1: Reboot the Server

Run this command:

```bash
sudo reboot
```

**Note:** Your connection will be disconnected. Wait 1-2 minutes for the server to fully reboot.

---

### Step 2: Reconnect to Server

After reboot, reconnect via SSH:

```bash
ssh sam@8.134.202.27
```

---

### Step 3: Run Verification Script

Once connected, run the automated verification script:

```bash
cd /home/sam/Github/AI-RSS-Hub
./verify_after_reboot.sh
```

This will check:
- ✅ Service status
- ✅ Auto-start enabled
- ✅ Port 8000 listening
- ✅ API health endpoint
- ✅ API status endpoint
- ✅ Feeds endpoint
- ✅ Service logs
- ✅ Database file

---

## 🧪 Manual Verification (Optional)

If you want to check manually:

```bash
# 1. Check service status
sudo systemctl status ai-rss-hub

# 2. Check if enabled
sudo systemctl is-enabled ai-rss-hub

# 3. Test API
curl http://localhost:8000/api/health

# 4. Test from external
curl http://8.134.202.27:8000/api/health

# 5. Check logs
sudo journalctl -u ai-rss-hub -n 20
```

---

## ✅ Expected Results

After reboot, you should see:

```
✅ Service: active (running)
✅ Auto-start: enabled
✅ Port 8000: LISTENING
✅ API Health: {"status": "ok"}
✅ API Status: {"status": "running"}
✅ Logs: Being written
✅ Database: File exists
```

---

## 🐛 If Something Fails

If auto-start doesn't work:

```bash
# Check what went wrong
sudo journalctl -u ai-rss-hub -n 50

# Start service manually
sudo systemctl start ai-rss-hub

# Check status
sudo systemctl status ai-rss-hub
```

---

## 📞 Quick Commands

```bash
# Reboot
sudo reboot

# After reconnecting:
cd ~/Github/AI-RSS-Hub
./verify_after_reboot.sh
```

---

**Ready to test? Run: `sudo reboot`** 🚀
