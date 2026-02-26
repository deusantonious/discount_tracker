from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram import Bot
from database import Database
from price_scraper import PriceScraper
import logging
from typing import List, Tuple
import asyncio

logger = logging.getLogger(__name__)


class PriceCheckScheduler:
    """Scheduler for periodic price checks."""

    def __init__(self, bot: Bot, database: Database, check_hour: int = 10):
        self.bot = bot
        self.database = database
        self.scraper = PriceScraper()
        self.scheduler = AsyncIOScheduler()
        self.check_hour = check_hour

    def start(self):
        """Start the scheduler and run an immediate price check."""
        # Run price check immediately on startup
        self.scheduler.add_job(
            self.check_all_prices,
            'date',  # one-time trigger
            id='startup_price_check'
        )

        # Schedule daily check at specified hour
        self.scheduler.add_job(
            self.check_all_prices,
            'cron',
            hour=self.check_hour,
            minute=0,
            id='daily_price_check'
        )

        # Also check every 6 hours as backup
        self.scheduler.add_job(
            self.check_all_prices,
            'interval',
            hours=6,
            id='periodic_price_check'
        )

        self.scheduler.start()
        logger.info(f"Scheduler started. Daily check at {self.check_hour}:00")

    async def check_all_prices(self):
        """Check prices for all active items."""
        logger.info("Starting scheduled price check...")

        items = self.database.get_all_active_items()
        logger.info(f"Found {len(items)} items to check")

        for item in items:
            try:
                await self.check_item_price(item)
                # Small delay to avoid overwhelming servers
                await asyncio.sleep(2)
            except Exception as e:
                logger.error(f"Error checking item {item[0]}: {e}")

    async def check_item_price(self, item: Tuple):
        """Check price for a single item and notify if changed."""
        item_id, user_id, url, title, current_price, last_checked = item

        logger.info(f"Checking item {item_id}: {url}")
        self.database.log_event('price_check', user_id, f'item_id={item_id}')

        # Scrape current price
        result = self.scraper.scrape_product(url)

        if not result['success']:
            self.database.log_event('scrape_fail', user_id, f'item_id={item_id} error={result.get("error", "unknown")}')
            logger.warning(f"Failed to scrape {url}: {result.get('error', 'Unknown error')}")
            return

        new_price = result['price']

        if new_price is None:
            self.database.log_event('scrape_fail', user_id, f'item_id={item_id} no_price')
            logger.warning(f"Could not extract price from {url}")
            return

        self.database.log_event('scrape_success', user_id, f'item_id={item_id} price={new_price}')

        # Update database
        price_changed = self.database.update_item_price(item_id, new_price)

        # Notify user if price changed
        if price_changed and current_price is not None:
            await self.notify_price_change(user_id, item_id, title or url, current_price, new_price)

    async def notify_price_change(self, user_id: int, item_id: int, title: str, old_price: float, new_price: float):
        """Send notification to user about price change."""
        try:
            price_diff = new_price - old_price
            price_change_pct = (price_diff / old_price) * 100

            # Determine emoji based on price change
            if price_diff < 0:
                emoji = "🔽"
                change_text = "decreased"
            else:
                emoji = "🔼"
                change_text = "increased"

            message = (
                f"{emoji} <b>Price {change_text}!</b>\n\n"
                f"<b>{title}</b>\n\n"
                f"Old price: ${old_price:.2f}\n"
                f"New price: ${new_price:.2f}\n"
                f"Change: ${abs(price_diff):.2f} ({abs(price_change_pct):.1f}%)\n\n"
                f"Item ID: {item_id}"
            )

            await self.bot.send_message(
                chat_id=user_id,
                text=message,
                parse_mode='HTML'
            )
            self.database.log_event('price_alert_sent', user_id, f'item_id={item_id} old={old_price} new={new_price}')

            logger.info(f"Notified user {user_id} about price change for item {item_id}")

        except Exception as e:
            logger.error(f"Failed to notify user {user_id}: {e}")

    def stop(self):
        """Stop the scheduler."""
        self.scheduler.shutdown()
        logger.info("Scheduler stopped")
