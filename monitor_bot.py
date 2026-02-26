"""
Monitor bot – a separate Telegram bot that reports usage analytics
of the main Price Tracker bot to the admin.

Requires env vars:
  MONITOR_BOT_TOKEN  – token from BotFather for the monitor bot
  ADMIN_USER_ID      – your Telegram user ID (only you can use this bot)
  DATABASE_PATH      – same DB as the main bot
"""

import os
import logging
import asyncio
from datetime import datetime

from dotenv import load_dotenv
from telegram import Update, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    filters,
)
from database import Database

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

database = Database(os.getenv("DATABASE_PATH", "price_tracker.db"))
ADMIN_USER_ID = int(os.getenv("ADMIN_USER_ID", "0"))


# ── Access control ───────────────────────────────────────────

def admin_only(func):
    """Decorator: silently ignore non-admin users."""
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id != ADMIN_USER_ID:
            await update.message.reply_text("⛔ Access denied.")
            return
        return await func(update, context)
    return wrapper


# ── Commands ─────────────────────────────────────────────────

@admin_only
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📊 <b>Price Tracker Monitor Bot</b>\n\n"
        "Commands:\n"
        "/stats – Full dashboard\n"
        "/users – User statistics\n"
        "/items – Item statistics\n"
        "/health – Scraper health\n"
        "/events – Recent event log\n"
        "/help – This message",
        parse_mode="HTML",
    )


@admin_only
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await start(update, context)


@admin_only
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Full dashboard."""
    s = database.get_stats()

    scrape_total = s["scrape_success_today"] + s["scrape_fail_today"]
    success_rate = (
        f"{s['scrape_success_today'] / scrape_total * 100:.0f}%"
        if scrape_total > 0
        else "N/A"
    )

    msg = (
        "📊 <b>Dashboard</b>\n"
        f"<i>{datetime.now().strftime('%Y-%m-%d %H:%M')}</i>\n\n"
        "👥 <b>Users</b>\n"
        f"  Total: {s['total_users']}\n"
        f"  New today: {s['new_users_today']}\n"
        f"  New this week: {s['new_users_week']}\n\n"
        "📦 <b>Items</b>\n"
        f"  Active: {s['active_items']}\n"
        f"  Added today: {s['items_added_today']}\n"
        f"  Deleted today: {s['items_deleted_today']}\n\n"
        "🔍 <b>Scraper</b>\n"
        f"  Checks today: {s['price_checks_today']}\n"
        f"  Success: {s['scrape_success_today']}  |  Fail: {s['scrape_fail_today']}\n"
        f"  Success rate: {success_rate}\n\n"
        "🔔 <b>Alerts sent today:</b> {alerts}\n"
    ).format(alerts=s["alerts_today"])

    # Top users
    if s["top_users"]:
        msg += "\n🏆 <b>Top users (by items)</b>\n"
        for uid, uname, fname, cnt in s["top_users"]:
            display = uname or fname or str(uid)
            msg += f"  • {display}: {cnt} items\n"

    await update.message.reply_text(msg, parse_mode="HTML")


@admin_only
async def users_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    s = database.get_stats()
    msg = (
        "👥 <b>User Statistics</b>\n\n"
        f"Total users: {s['total_users']}\n"
        f"New today: {s['new_users_today']}\n"
        f"New this week: {s['new_users_week']}\n"
    )
    if s["top_users"]:
        msg += "\n🏆 <b>Most active</b>\n"
        for uid, uname, fname, cnt in s["top_users"]:
            display = uname or fname or str(uid)
            msg += f"  • {display}: {cnt} items\n"
    await update.message.reply_text(msg, parse_mode="HTML")


@admin_only
async def items_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    s = database.get_stats()
    await update.message.reply_text(
        "📦 <b>Item Statistics</b>\n\n"
        f"Active items: {s['active_items']}\n"
        f"Added today: {s['items_added_today']}\n"
        f"Deleted today: {s['items_deleted_today']}\n",
        parse_mode="HTML",
    )


@admin_only
async def health_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    s = database.get_stats()
    scrape_total = s["scrape_success_today"] + s["scrape_fail_today"]
    rate = (
        f"{s['scrape_success_today'] / scrape_total * 100:.0f}%"
        if scrape_total > 0
        else "N/A"
    )
    await update.message.reply_text(
        "🔍 <b>Scraper Health</b>\n\n"
        f"Price checks today: {s['price_checks_today']}\n"
        f"Successful scrapes: {s['scrape_success_today']}\n"
        f"Failed scrapes: {s['scrape_fail_today']}\n"
        f"Success rate: {rate}\n\n"
        f"🔔 Alerts sent today: {s['alerts_today']}",
        parse_mode="HTML",
    )


@admin_only
async def events_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    s = database.get_stats()
    if not s["events_24h"]:
        await update.message.reply_text("No events in the last 24 hours.")
        return
    msg = "📋 <b>Events (last 24h)</b>\n\n"
    for etype, cnt in s["events_24h"]:
        msg += f"  • <code>{etype}</code>: {cnt}\n"
    await update.message.reply_text(msg, parse_mode="HTML")


# ── Daily report job ─────────────────────────────────────────

async def send_daily_report(context: ContextTypes.DEFAULT_TYPE):
    """Send a daily summary to the admin."""
    s = database.get_stats()
    scrape_total = s["scrape_success_today"] + s["scrape_fail_today"]
    rate = (
        f"{s['scrape_success_today'] / scrape_total * 100:.0f}%"
        if scrape_total > 0
        else "N/A"
    )
    msg = (
        "📊 <b>Daily Report</b>\n"
        f"<i>{datetime.now().strftime('%Y-%m-%d')}</i>\n\n"
        f"👥 Users: {s['total_users']} total, +{s['new_users_today']} today\n"
        f"📦 Items: {s['active_items']} active, +{s['items_added_today']} added\n"
        f"🔍 Scraper: {rate} success ({s['scrape_success_today']}/{scrape_total})\n"
        f"🔔 Alerts sent: {s['alerts_today']}\n"
    )
    try:
        await context.bot.send_message(
            chat_id=ADMIN_USER_ID, text=msg, parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Failed to send daily report: {e}")


# ── Main ─────────────────────────────────────────────────────

def main():
    token = os.getenv("MONITOR_BOT_TOKEN")
    if not token:
        logger.error("MONITOR_BOT_TOKEN not set!")
        return
    if ADMIN_USER_ID == 0:
        logger.error("ADMIN_USER_ID not set!")
        return

    async def post_init(app):
        await app.bot.set_my_commands([
            BotCommand("stats", "Full dashboard"),
            BotCommand("users", "User statistics"),
            BotCommand("items", "Item statistics"),
            BotCommand("health", "Scraper health"),
            BotCommand("events", "Recent event log"),
            BotCommand("help", "Show help"),
        ])
        # Daily report at 21:00
        app.job_queue.run_daily(
            send_daily_report,
            time=datetime.strptime("21:00", "%H:%M").time(),
            name="daily_report",
        )
        logger.info("Monitor bot ready – daily report scheduled at 21:00")

    application = Application.builder().token(token).post_init(post_init).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_cmd))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CommandHandler("users", users_cmd))
    application.add_handler(CommandHandler("items", items_cmd))
    application.add_handler(CommandHandler("health", health_cmd))
    application.add_handler(CommandHandler("events", events_cmd))

    logger.info("Monitor bot started!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
