import os
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)
from database import Database
from price_scraper import PriceScraper
from scheduler import PriceCheckScheduler
from bot_metadata import setup_bot_metadata

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize components
database = Database(os.getenv('DATABASE_PATH', 'price_tracker.db'))
scraper = PriceScraper()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command."""
    user = update.effective_user
    database.add_user(user.id, user.username, user.first_name)

    welcome_message = (
        f"👋 Hello, {user.first_name}!\n\n"
        "I'm a Price Tracker Bot. I can help you track prices of products from online stores.\n\n"
        "<b>How to use:</b>\n"
        "1. Send me a product URL\n"
        "2. I'll track the price daily\n"
        "3. You'll get notified when price changes\n\n"
        "<b>Commands:</b>\n"
        "/list - View your tracked items\n"
        "/help - Show this help message"
    )

    await update.message.reply_text(welcome_message, parse_mode='HTML')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command."""
    help_text = (
        "<b>📋 Available Commands:</b>\n\n"
        "/start - Start the bot\n"
        "/list - View all your tracked items\n"
        "/help - Show this help message\n\n"
        "<b>📌 How to track a product:</b>\n"
        "Just send me a product URL from any online store.\n\n"
        "I'll automatically detect the price and title, then start tracking it for you.\n\n"
        "<b>🔔 Notifications:</b>\n"
        "You'll receive a message whenever a tracked item's price changes."
    )

    await update.message.reply_text(help_text, parse_mode='HTML')


async def list_items(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /list command - show user's tracked items."""
    user_id = update.effective_user.id
    items = database.get_user_items(user_id)

    if not items:
        await update.message.reply_text(
            "📭 You don't have any tracked items yet.\n\n"
            "Send me a product URL to start tracking!"
        )
        return

    message = "<b>📦 Your Tracked Items:</b>\n\n"

    for item in items:
        item_id, url, title, current_price, initial_price, last_checked, created_at = item

        # Calculate price change
        price_change = ""
        if initial_price and current_price:
            diff = current_price - initial_price
            if abs(diff) > 0.01:
                emoji = "🔽" if diff < 0 else "🔼"
                price_change = f" {emoji} ${abs(diff):.2f}"

        display_price = current_price if current_price else 0
        message += (
            f"<b>ID {item_id}:</b> {title or 'No title'}\n"
            f"💰 Current: ${display_price:.2f}{price_change}\n"
            f"🔗 <a href='{url}'>View Product</a>\n\n"
        )

    keyboard = [
        [InlineKeyboardButton("🗑 Delete Item", callback_data="delete_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        message,
        parse_mode='HTML',
        reply_markup=reply_markup,
        disable_web_page_preview=True
    )


async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming URLs."""
    user_id = update.effective_user.id
    url = update.message.text.strip()

    # Basic URL validation
    if not url.startswith(('http://', 'https://')):
        await update.message.reply_text(
            "❌ Please send a valid URL starting with http:// or https://"
        )
        return

    # Send "processing" message
    processing_msg = await update.message.reply_text("🔍 Analyzing product page...")

    # Scrape product info
    result = scraper.scrape_product(url)

    if not result['success']:
        await processing_msg.edit_text(
            f"❌ Failed to fetch product information.\n\n"
            f"Error: {result.get('error', 'Unknown error')}\n\n"
            "Please make sure the URL is accessible and try again."
        )
        return

    title = result['title']
    price = result['price']

    if price is None:
        await processing_msg.edit_text(
            "⚠️ I found the page but couldn't detect the price.\n\n"
            "This might happen if:\n"
            "- The page requires JavaScript\n"
            "- The site has anti-bot protection\n"
            "- The price format is unusual\n\n"
            "Try another product or store."
        )
        return

    # Add to database
    item_id = database.add_tracked_item(user_id, url, title, price)

    domain = scraper.get_domain(url)

    success_message = (
        "✅ <b>Product added to tracking!</b>\n\n"
        f"<b>Title:</b> {title or 'N/A'}\n"
        f"<b>Price:</b> ${price:.2f}\n"
        f"<b>Store:</b> {domain}\n"
        f"<b>Item ID:</b> {item_id}\n\n"
        "I'll check this product daily and notify you about price changes."
    )

    keyboard = [
        [InlineKeyboardButton("📋 View All Items", callback_data="view_list")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await processing_msg.edit_text(
        success_message,
        parse_mode='HTML',
        reply_markup=reply_markup
    )


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks."""
    query = update.callback_query
    await query.answer()

    if query.data == "view_list":
        user_id = query.from_user.id
        items = database.get_user_items(user_id)

        if not items:
            await query.edit_message_text("📭 You don't have any tracked items yet.")
            return

        message = "<b>📦 Your Tracked Items:</b>\n\n"

        for item in items:
            item_id, url, title, current_price, initial_price, last_checked, created_at = item

            price_change = ""
            if initial_price and current_price:
                diff = current_price - initial_price
                if abs(diff) > 0.01:
                    emoji = "🔽" if diff < 0 else "🔼"
                    price_change = f" {emoji} ${abs(diff):.2f}"

            display_price = current_price if current_price else 0
            message += (
                f"<b>ID {item_id}:</b> {title or 'No title'}\n"
                f"💰 Current: ${display_price:.2f}{price_change}\n"
                f"🔗 <a href='{url}'>View Product</a>\n\n"
            )

        keyboard = [
            [InlineKeyboardButton("🗑 Delete Item", callback_data="delete_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            message,
            parse_mode='HTML',
            reply_markup=reply_markup,
            disable_web_page_preview=True
        )

    elif query.data == "delete_menu":
        await query.edit_message_text(
            "To delete an item, use the command:\n"
            "<code>/delete [item_id]</code>\n\n"
            "You can find the item ID in your items list.",
            parse_mode='HTML'
        )


async def delete_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /delete command."""
    user_id = update.effective_user.id

    if not context.args:
        await update.message.reply_text(
            "Please specify an item ID.\n"
            "Usage: <code>/delete [item_id]</code>",
            parse_mode='HTML'
        )
        return

    try:
        item_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("❌ Invalid item ID. Please use a number.")
        return

    # Verify item belongs to user
    item = database.get_item_by_id(item_id)

    if not item:
        await update.message.reply_text("❌ Item not found.")
        return

    if item[1] != user_id:
        await update.message.reply_text("❌ You don't have permission to delete this item.")
        return

    # Delete item
    success = database.delete_item(item_id, user_id)

    if success:
        await update.message.reply_text(f"✅ Item #{item_id} has been deleted.")
    else:
        await update.message.reply_text("❌ Failed to delete item.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle non-URL messages."""
    await update.message.reply_text(
        "Please send me a product URL to track.\n\n"
        "Example: https://example.com/product/123\n\n"
        "Use /help to see available commands."
    )


def main():
    """Start the bot."""
    token = os.getenv('TELEGRAM_BOT_TOKEN')

    if not token:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables!")
        return

    # Initialize scheduler (started inside post_init when event loop exists)
    check_hour = int(os.getenv('CHECK_HOUR', '10'))

    async def post_init(app):
        await setup_bot_metadata(app.bot)
        scheduler = PriceCheckScheduler(app.bot, database, check_hour)
        scheduler.start()

    # Create application
    application = Application.builder().token(token).post_init(post_init).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("list", list_items))
    application.add_handler(CommandHandler("delete", delete_item))
    application.add_handler(CallbackQueryHandler(button_callback))

    # URL handler (matches http:// or https://)
    application.add_handler(MessageHandler(
        filters.TEXT & filters.Regex(r'^https?://'),
        handle_url
    ))

    # General message handler
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_message
    ))

    # Start bot
    logger.info("Bot started!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
