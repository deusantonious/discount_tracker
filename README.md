# Telegram Price Tracker Bot

A Telegram bot that tracks product prices from online stores and notifies users when prices change.

## Features

- 🔗 Track products by sending URLs
- 💰 Automatic price detection
- 📊 Daily price monitoring
- 🔔 Instant notifications on price changes
- 📋 List all tracked items
- 🗑 Remove items from tracking

## Setup

### 1. Prerequisites

- Python 3.8+
- Telegram Bot Token (get from [@BotFather](https://t.me/botfather))

### 2. Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Or use virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configuration

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Edit `.env` and add your bot token:

```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
DATABASE_PATH=price_tracker.db
CHECK_HOUR=10
```

**Configuration options:**
- `TELEGRAM_BOT_TOKEN`: Your bot token from BotFather
- `DATABASE_PATH`: SQLite database file path (default: `price_tracker.db`)
- `CHECK_HOUR`: Hour of day to check prices (0-23, default: 10 = 10:00 AM)

### 4. Running the Bot

```bash
python bot.py
```

The bot will:
- Start listening for messages
- Check prices daily at the configured hour
- Also check every 6 hours as backup

## Usage

### Commands

- `/start` - Start the bot and see welcome message
- `/help` - Show help message with all commands
- `/list` - View all your tracked items
- `/delete [item_id]` - Delete a tracked item

### Tracking a Product

1. Find a product on any online store
2. Copy the product URL
3. Send it to the bot
4. The bot will:
   - Extract the title and price
   - Add it to your tracking list
   - Start monitoring it daily

### Example

```
User: https://www.amazon.com/dp/B08N5WRWNW
Bot: ✅ Product added to tracking!

Title: Echo Dot (4th Gen)
Price: $49.99
Store: www.amazon.com
Item ID: 1

I'll check this product daily and notify you about price changes.
```

## Price Scraping

The bot attempts to extract prices using multiple methods:

1. **Meta tags** (og:price:amount, product:price:amount)
2. **Common CSS selectors** (classes/IDs containing "price")
3. **Regex patterns** (currency symbols with numbers)

**Supported formats:**
- $1,234.56
- €1.234,56
- 1,234.56 USD
- And many more

**Note:** Some websites may block automated scraping or require JavaScript. The bot works best with standard e-commerce sites.

## Database Structure

### Tables

**users**
- user_id (PRIMARY KEY)
- username
- first_name
- created_at

**tracked_items**
- id (PRIMARY KEY)
- user_id (FOREIGN KEY)
- url
- title
- current_price
- initial_price
- last_checked
- created_at
- is_active

**price_history**
- id (PRIMARY KEY)
- item_id (FOREIGN KEY)
- price
- checked_at

## Project Structure

```
tg_bit/
├── bot.py                 # Main bot logic and handlers
├── database.py            # Database operations
├── price_scraper.py       # Web scraping logic
├── scheduler.py           # Price check scheduling
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── .gitignore            # Git ignore rules
└── README.md             # This file
```

## Deployment

### Local Development

```bash
python bot.py
```

### Production (Linux Server)

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set up as a service (systemd):**

Create `/etc/systemd/system/price-tracker-bot.service`:

```ini
[Unit]
Description=Telegram Price Tracker Bot
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/tg_bit
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/python bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

3. **Start the service:**
```bash
sudo systemctl enable price-tracker-bot
sudo systemctl start price-tracker-bot
sudo systemctl status price-tracker-bot
```

### Using Docker (Optional)

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "bot.py"]
```

Run with:
```bash
docker build -t price-tracker-bot .
docker run -d --name price-bot --env-file .env price-tracker-bot
```

## Troubleshooting

### Bot doesn't respond
- Check if token is correct in `.env`
- Ensure bot.py is running without errors
- Check logs for error messages

### Price not detected
- Some sites block automated access
- Site may require JavaScript rendering
- Try different product URLs
- Check the HTML structure manually

### Daily checks not working
- Verify `CHECK_HOUR` in `.env`
- Check scheduler logs
- Ensure bot process stays running

## Limitations

- May not work with JavaScript-heavy sites
- Some sites have anti-bot protection
- Rate limiting may affect frequent checks
- Price formats vary by region/site

## Future Improvements

- [ ] Support for more price formats
- [ ] Configurable check frequency per item
- [ ] Price threshold alerts (notify only if change > X%)
- [ ] Historical price charts
- [ ] Multiple currency support
- [ ] Proxy support for blocked sites
- [ ] Browser automation (Selenium/Playwright) for JS sites

## License

MIT License - feel free to use and modify!

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Support

For issues or questions:
- Check existing issues
- Create a new issue with details
- Include error logs and example URLs
