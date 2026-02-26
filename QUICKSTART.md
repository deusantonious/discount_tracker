# Quick Start Guide

## 1️⃣ Get Your Bot Token

1. Open Telegram and search for **@BotFather**
2. Send `/newbot` command
3. Follow instructions to create your bot
4. Copy the token (looks like: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

## 2️⃣ Configure the Bot

```bash
# Create .env file
cp .env.example .env

# Edit and add your token
nano .env
```

Change this line:
```
TELEGRAM_BOT_TOKEN=your_bot_token_here
```

To:
```
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
```

Save and exit (Ctrl+X, then Y, then Enter)

## 3️⃣ Choose Your Deployment

### Option A: Run Locally (Testing)

```bash
# Install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run bot
python bot.py
```

Bot will run as long as terminal is open.

---

### Option B: VPS Server (24/7 Operation)

**Easiest:** Use the automated script!

```bash
# Make script executable
chmod +x deploy_vps.sh

# Run deployment
./deploy_vps.sh
```

The script will:
- ✅ Install dependencies
- ✅ Create virtual environment
- ✅ Set up systemd service
- ✅ Start the bot
- ✅ Enable auto-restart

**Manual setup:** See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

---

### Option C: Docker

```bash
# Create .env file with your token
cp .env.example .env
nano .env

# Start with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

---

## 4️⃣ Test Your Bot

1. Open Telegram
2. Search for your bot username (the one you created in BotFather)
3. Send `/start` command
4. Send a product URL (e.g., from Amazon, eBay, etc.)

Example:
```
/start
→ Bot sends welcome message

https://www.amazon.com/dp/B08N5WRWNW
→ Bot tracks the product
```

---

## 5️⃣ Using the Bot

### Commands

- `/start` - Start the bot
- `/help` - Show help
- `/list` - View tracked items
- `/delete [id]` - Remove item

### Track a Product

Just send any product URL:
- Amazon: `https://amazon.com/...`
- eBay: `https://ebay.com/...`
- Any online store with visible prices

---

## 🔧 Management (VPS/systemd)

```bash
# Check if bot is running
sudo systemctl status price-bot

# Restart bot
sudo systemctl restart price-bot

# View logs
sudo journalctl -u price-bot -f

# Stop bot
sudo systemctl stop price-bot
```

---

## 🐛 Troubleshooting

### Bot doesn't respond

1. **Check token is correct:**
```bash
cat .env
```

2. **Check bot is running:**
```bash
# Local
ps aux | grep "python bot.py"

# VPS/systemd
sudo systemctl status price-bot
```

3. **Check logs for errors:**
```bash
# Local
# Look at terminal output

# VPS/systemd
sudo journalctl -u price-bot -n 50
```

### Price not detected

Some sites don't work well with scraping:
- Try another product from same store
- Try a different store
- Check if URL is accessible in browser

### Bot stops after closing terminal

- Use Option B (VPS with systemd service)
- Or run with `nohup python bot.py &`

---

## 📊 Where is my data?

All data is stored in SQLite database:
```bash
# Default location
./price_tracker.db

# Backup your database
cp price_tracker.db price_tracker.db.backup
```

---

## 🆘 Need More Help?

- See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment options
- See [README.md](README.md) for full documentation
- Check logs for specific error messages

---

## ✅ Recommended Setup

For reliable 24/7 operation:

1. **Get a cheap VPS** ($5-6/month)
   - DigitalOcean
   - Linode
   - Vultr
   - Hetzner

2. **Run deployment script:**
```bash
./deploy_vps.sh
```

3. **Done!** Bot runs 24/7, auto-restarts if crashed

---

## 🎉 You're Ready!

Your bot is now tracking prices and will notify you of changes!
