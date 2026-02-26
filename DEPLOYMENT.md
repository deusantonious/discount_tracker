# Deployment Guide

## Option 1: Local Machine (Testing)

Perfect for testing and development.

### Steps:

1. **Create .env file:**
```bash
cp .env.example .env
```

2. **Edit .env and add your bot token:**
```env
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
DATABASE_PATH=price_tracker.db
CHECK_HOUR=10
```

3. **Install dependencies:**
```bash
python3 -m venv venv
source venv/bin/activate  # On Mac/Linux
pip install -r requirements.txt
```

4. **Run the bot:**
```bash
python bot.py
```

Keep the terminal open. Bot will stop when you close it.

---

## Option 2: VPS/Cloud Server (Recommended)

Best for 24/7 operation. Works on:
- DigitalOcean ($6/month)
- AWS EC2 (Free tier available)
- Linode, Vultr, Hetzner
- Any Linux VPS

### Setup on Ubuntu/Debian:

1. **Connect to your server:**
```bash
ssh user@your-server-ip
```

2. **Install Python and dependencies:**
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git
```

3. **Clone or upload your project:**
```bash
# Option A: Upload files
# Use SCP or SFTP to upload the tg_bit folder

# Option B: Git (if you have a repo)
git clone your-repo-url
cd tg_bit
```

4. **Create virtual environment:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

5. **Configure environment:**
```bash
cp .env.example .env
nano .env  # Add your bot token
```

6. **Test run:**
```bash
python bot.py
```

Press Ctrl+C to stop.

7. **Set up as a system service (runs 24/7):**

Create service file:
```bash
sudo nano /etc/systemd/system/price-bot.service
```

Add this content (replace paths with your actual paths):
```ini
[Unit]
Description=Telegram Price Tracker Bot
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/home/YOUR_USERNAME/tg_bit
Environment="PATH=/home/YOUR_USERNAME/tg_bit/venv/bin"
ExecStart=/home/YOUR_USERNAME/tg_bit/venv/bin/python bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

8. **Enable and start the service:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable price-bot
sudo systemctl start price-bot
```

9. **Check status:**
```bash
sudo systemctl status price-bot
```

10. **View logs:**
```bash
sudo journalctl -u price-bot -f
```

### Managing the service:
```bash
sudo systemctl start price-bot    # Start
sudo systemctl stop price-bot     # Stop
sudo systemctl restart price-bot  # Restart
sudo systemctl status price-bot   # Check status
```

---

## Option 3: Docker

If you prefer containerization.

### Create Dockerfile:

```bash
nano Dockerfile
```

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Run bot
CMD ["python", "bot.py"]
```

### Create docker-compose.yml:

```bash
nano docker-compose.yml
```

```yaml
version: '3.8'

services:
  price-bot:
    build: .
    container_name: telegram-price-bot
    restart: unless-stopped
    env_file:
      - .env
    volumes:
      - ./data:/app/data
    environment:
      - DATABASE_PATH=/app/data/price_tracker.db
```

### Deploy with Docker:

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down

# Restart
docker-compose restart
```

---

## Option 4: Heroku (Free/Paid Cloud)

Good for small projects, but Heroku removed free tier.

### Steps:

1. **Install Heroku CLI**
2. **Create Procfile:**
```bash
echo "worker: python bot.py" > Procfile
```

3. **Create runtime.txt:**
```bash
echo "python-3.11.0" > runtime.txt
```

4. **Deploy:**
```bash
heroku login
heroku create your-app-name
heroku config:set TELEGRAM_BOT_TOKEN=your_token
git push heroku main
heroku ps:scale worker=1
```

---

## Option 5: Railway.app (Easy Cloud, Free Tier)

Modern alternative to Heroku.

### Steps:

1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Add environment variables:
   - `TELEGRAM_BOT_TOKEN`
   - `DATABASE_PATH=price_tracker.db`
   - `CHECK_HOUR=10`
6. Deploy automatically

---

## Option 6: Raspberry Pi (Home Server)

Perfect if you have a Raspberry Pi.

### Steps:

1. **SSH to your Pi:**
```bash
ssh pi@raspberrypi.local
```

2. **Install dependencies:**
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv
```

3. **Upload project files** (use SCP or USB)

4. **Follow VPS setup steps** (Option 2)

5. **Set up autostart:**
```bash
crontab -e
```

Add this line:
```
@reboot cd /home/pi/tg_bit && /home/pi/tg_bit/venv/bin/python bot.py
```

---

## Recommended Setup: VPS with systemd

**Why?**
- ✅ Full control
- ✅ Runs 24/7
- ✅ Auto-restart on failure
- ✅ Low cost ($5-10/month)
- ✅ Easy to manage

**Providers:**
- **DigitalOcean** - $6/month droplet
- **Linode** - $5/month
- **Vultr** - $5/month
- **Hetzner** - €4/month (cheapest)

---

## Monitoring & Maintenance

### Check if bot is running:
```bash
sudo systemctl status price-bot
```

### View recent logs:
```bash
sudo journalctl -u price-bot -n 100
```

### View live logs:
```bash
sudo journalctl -u price-bot -f
```

### Restart after code changes:
```bash
cd /path/to/tg_bit
source venv/bin/activate
git pull  # if using git
sudo systemctl restart price-bot
```

### Backup database:
```bash
cp price_tracker.db price_tracker.db.backup
# Or automated:
0 3 * * * cp /path/to/price_tracker.db /path/to/backups/price_tracker_$(date +\%Y\%m\%d).db
```

---

## Troubleshooting

### Bot doesn't start:
```bash
# Check logs
sudo journalctl -u price-bot -n 50

# Common issues:
# 1. Wrong token → Check .env
# 2. Missing dependencies → pip install -r requirements.txt
# 3. Permission issues → Check file ownership
```

### Bot stops randomly:
```bash
# Check system resources
free -h
df -h

# Bot will auto-restart with systemd
```

### Price checks not working:
```bash
# Check scheduler logs
sudo journalctl -u price-bot | grep "Scheduler"

# Verify CHECK_HOUR in .env
```

---

## Security Best Practices

1. **Keep .env secure:**
```bash
chmod 600 .env
```

2. **Don't commit .env to git:**
Already in .gitignore

3. **Update dependencies regularly:**
```bash
pip install --upgrade -r requirements.txt
```

4. **Use firewall:**
```bash
sudo ufw enable
sudo ufw allow ssh
```

5. **Regular backups:**
Set up automated database backups

---

## Need Help?

Choose your deployment method and I'll provide detailed steps!
