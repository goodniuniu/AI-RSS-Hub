#!/bin/bash
# AI-RSS-Hub Service Installation Script
# This script installs systemd service for auto-start on boot

set -e

echo "================================"
echo "  AI-RSS-Hub Service Installer"
echo "================================"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Error: This script must be run as root (use sudo)"
    echo "   Command: sudo bash install_service.sh"
    exit 1
fi

SERVICE_FILE="ai-rss-hub.service"
SERVICE_PATH="/etc/systemd/system/${SERVICE_FILE}"
APP_DIR="/home/sam/Github/AI-RSS-Hub"
APP_USER="sam"

echo "📋 Configuration:"
echo "   Service File: ${SERVICE_FILE}"
echo "   Install Path: ${SERVICE_PATH}"
echo "   App Directory: ${APP_DIR}"
echo "   Run as User: ${APP_USER}"
echo ""

# Check if service file exists
if [ ! -f "${SERVICE_FILE}" ]; then
    echo "❌ Error: Service file '${SERVICE_FILE}' not found!"
    echo "   Please run this script from the AI-RSS-Hub directory"
    exit 1
fi

# Check if app directory exists
if [ ! -d "${APP_DIR}" ]; then
    echo "❌ Error: Application directory '${APP_DIR}' not found!"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "${APP_DIR}/venv" ]; then
    echo "❌ Error: Virtual environment not found at '${APP_DIR}/venv'"
    echo "   Please create it first: python3 -m venv venv"
    exit 1
fi

echo "⏳ Step 1: Stopping existing service (if running)..."
systemctl stop ai-rss-hub 2>/dev/null || echo "   Service not running yet"
echo "   ✅ Done"
echo ""

echo "⏳ Step 2: Copying service file..."
cp "${SERVICE_FILE}" "${SERVICE_PATH}"
chmod 644 "${SERVICE_PATH}"
echo "   ✅ Service file installed to ${SERVICE_PATH}"
echo ""

echo "⏳ Step 3: Reloading systemd daemon..."
systemctl daemon-reload
echo "   ✅ Done"
echo ""

echo "⏳ Step 4: Enabling service to start on boot..."
systemctl enable ai-rss-hub
echo "   ✅ Service enabled"
echo ""

echo "⏳ Step 5: Starting service..."
systemctl start ai-rss-hub
sleep 2
echo "   ✅ Service started"
echo ""

echo "⏳ Step 6: Checking service status..."
systemctl status ai-rss-hub --no-pager
echo ""

echo "================================"
echo "  ✅ Installation Complete!"
echo "================================"
echo ""
echo "Service Management Commands:"
echo "  Check status:  sudo systemctl status ai-rss-hub"
echo "  Start service: sudo systemctl start ai-rss-hub"
echo "  Stop service:  sudo systemctl stop ai-rss-hub"
echo "  Restart:       sudo systemctl restart ai-rss-hub"
echo "  View logs:     sudo journalctl -u ai-rss-hub -f"
echo "  View all logs: sudo journalctl -u ai-rss-hub"
echo ""
echo "📖 Quick Test:"
echo "  curl http://localhost:8000/api/health"
echo ""
