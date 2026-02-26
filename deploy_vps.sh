#!/bin/bash

# Automated VPS deployment script for Telegram Price Tracker Bot
# Usage: ./deploy_vps.sh

set -e

echo "🚀 Telegram Price Tracker Bot - VPS Deployment Script"
echo "======================================================"
echo ""

# Get current directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found!"
    echo "Creating from .env.example..."
    cp .env.example .env
    echo ""
    echo "Please edit .env and add your TELEGRAM_BOT_TOKEN"
    echo "Then run this script again."
    echo ""
    echo "Edit with: nano .env"
    exit 1
fi

# Check if token is set
if grep -q "your_bot_token_here" .env; then
    echo "❌ Please set your TELEGRAM_BOT_TOKEN in .env file"
    echo "Edit with: nano .env"
    exit 1
fi

echo "✅ .env file found"
echo ""

# Install Python and dependencies
echo "📦 Installing system dependencies..."
if command -v apt-get &> /dev/null; then
    sudo apt-get update
    sudo apt-get install -y python3 python3-pip python3-venv
elif command -v yum &> /dev/null; then
    sudo yum install -y python3 python3-pip
fi

echo "✅ System dependencies installed"
echo ""

# Create virtual environment
echo "🐍 Setting up Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

echo "✅ Virtual environment ready"
echo ""

# Install Python packages
echo "📚 Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Python packages installed"
echo ""

# Test bot
echo "🧪 Testing bot configuration..."
timeout 5 python bot.py || true

echo ""
echo "📋 Setup system service? (runs 24/7, auto-restart)"
read -p "Deploy as systemd service? (y/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    SERVICE_FILE="/etc/systemd/system/price-bot.service"
    USER=$(whoami)
    WORKING_DIR="$SCRIPT_DIR"
    VENV_PYTHON="$SCRIPT_DIR/venv/bin/python"

    echo "Creating systemd service..."

    sudo tee $SERVICE_FILE > /dev/null <<EOF
[Unit]
Description=Telegram Price Tracker Bot
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$WORKING_DIR
Environment="PATH=$SCRIPT_DIR/venv/bin"
ExecStart=$VENV_PYTHON bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    sudo systemctl enable price-bot
    sudo systemctl start price-bot

    echo ""
    echo "✅ Service installed and started!"
    echo ""
    echo "📊 Service status:"
    sudo systemctl status price-bot --no-pager

    echo ""
    echo "Useful commands:"
    echo "  sudo systemctl status price-bot    # Check status"
    echo "  sudo systemctl restart price-bot   # Restart bot"
    echo "  sudo systemctl stop price-bot      # Stop bot"
    echo "  sudo journalctl -u price-bot -f    # View logs"
else
    echo ""
    echo "Skipping service installation."
    echo ""
    echo "To run manually:"
    echo "  source venv/bin/activate"
    echo "  python bot.py"
fi

echo ""
echo "🎉 Deployment complete!"
echo ""
echo "Test your bot on Telegram: @your_bot_username"
