"""
Bot name, description, and commands translations.
Sets per-language metadata via Telegram Bot API so users see
the bot in their own language automatically.

Languages: en, ru, uk, es, pt, ar, hi, fr, de, id, tr
"""

import logging
from telegram import Bot, BotCommand

logger = logging.getLogger(__name__)

# ── Translations ─────────────────────────────────────────────

BOT_NAMES = {
    "en": "Price Tracker",
    "ru": "Трекер Цен",
    "uk": "Трекер Цін",
    "es": "Rastreador de Precios",
    "pt": "Rastreador de Preços",
    "ar": "متتبع الأسعار",
    "hi": "प्राइस ट्रैकर",
    "fr": "Suivi des Prix",
    "de": "Preis-Tracker",
    "id": "Pelacak Harga",
    "tr": "Fiyat Takipçisi",
}

BOT_DESCRIPTIONS = {
    "en": (
        "Track product prices from online stores and get notified "
        "when they change!\n\n"
        "Send a product URL and I'll monitor its price for you daily."
    ),
    "ru": (
        "Отслеживайте цены на товары из интернет-магазинов и получайте "
        "уведомления при изменении цены!\n\n"
        "Отправьте ссылку на товар, и я буду ежедневно проверять его цену."
    ),
    "uk": (
        "Відстежуйте ціни на товари з інтернет-магазинів та отримуйте "
        "сповіщення при зміні ціни!\n\n"
        "Надішліть посилання на товар, і я щодня перевірятиму його ціну."
    ),
    "es": (
        "¡Rastrea los precios de productos de tiendas en línea y recibe "
        "notificaciones cuando cambien!\n\n"
        "Envía una URL de producto y lo monitorearé diariamente."
    ),
    "pt": (
        "Acompanhe os preços de produtos de lojas online e receba "
        "notificações quando mudarem!\n\n"
        "Envie um link de produto e eu vou monitorar o preço diariamente."
    ),
    "ar": (
        "تتبّع أسعار المنتجات من المتاجر الإلكترونية واحصل على إشعارات "
        "عند تغيّر الأسعار!\n\n"
        "أرسل رابط المنتج وسأراقب سعره يوميًا."
    ),
    "hi": (
        "ऑनलाइन स्टोर से प्रोडक्ट की कीमतें ट्रैक करें और कीमत बदलने पर "
        "नोटिफिकेशन पाएं!\n\n"
        "एक प्रोडक्ट URL भेजें और मैं हर दिन उसकी कीमत जाँचूँगा।"
    ),
    "fr": (
        "Suivez les prix des produits des boutiques en ligne et recevez "
        "des notifications lors de changements de prix !\n\n"
        "Envoyez une URL de produit et je surveillerai son prix quotidiennement."
    ),
    "de": (
        "Verfolge Produktpreise aus Online-Shops und erhalte "
        "Benachrichtigungen bei Preisänderungen!\n\n"
        "Sende eine Produkt-URL und ich überwache den Preis täglich."
    ),
    "id": (
        "Lacak harga produk dari toko online dan dapatkan notifikasi "
        "saat harga berubah!\n\n"
        "Kirim URL produk dan saya akan memantau harganya setiap hari."
    ),
    "tr": (
        "Çevrimiçi mağazalardaki ürün fiyatlarını takip edin ve fiyat "
        "değiştiğinde bildirim alın!\n\n"
        "Bir ürün bağlantısı gönderin, fiyatını her gün kontrol edeceğim."
    ),
}

BOT_SHORT_DESCRIPTIONS = {
    "en": "Track prices & get notified about deals",
    "ru": "Отслеживание цен и уведомления о скидках",
    "uk": "Відстеження цін та сповіщення про знижки",
    "es": "Rastrea precios y recibe alertas de ofertas",
    "pt": "Rastreie preços e receba alertas de ofertas",
    "ar": "تتبّع الأسعار واحصل على تنبيهات العروض",
    "hi": "कीमतें ट्रैक करें और डील की सूचना पाएं",
    "fr": "Suivez les prix et recevez des alertes de bons plans",
    "de": "Preise verfolgen & über Angebote benachrichtigt werden",
    "id": "Lacak harga & dapatkan pemberitahuan promo",
    "tr": "Fiyatları takip edin ve fırsatlardan haberdar olun",
}

BOT_COMMANDS = {
    "en": [
        ("start", "Start the bot"),
        ("list", "View tracked items"),
        ("delete", "Delete a tracked item"),
        ("help", "Show help"),
    ],
    "ru": [
        ("start", "Запустить бота"),
        ("list", "Мои товары"),
        ("delete", "Удалить товар"),
        ("help", "Помощь"),
    ],
    "uk": [
        ("start", "Запустити бота"),
        ("list", "Мої товари"),
        ("delete", "Видалити товар"),
        ("help", "Допомога"),
    ],
    "es": [
        ("start", "Iniciar el bot"),
        ("list", "Ver productos rastreados"),
        ("delete", "Eliminar un producto"),
        ("help", "Mostrar ayuda"),
    ],
    "pt": [
        ("start", "Iniciar o bot"),
        ("list", "Ver produtos rastreados"),
        ("delete", "Remover um produto"),
        ("help", "Mostrar ajuda"),
    ],
    "ar": [
        ("start", "بدء البوت"),
        ("list", "عرض المنتجات المتتبعة"),
        ("delete", "حذف منتج"),
        ("help", "عرض المساعدة"),
    ],
    "hi": [
        ("start", "बोट शुरू करें"),
        ("list", "ट्रैक किए गए आइटम देखें"),
        ("delete", "आइटम हटाएं"),
        ("help", "मदद दिखाएं"),
    ],
    "fr": [
        ("start", "Démarrer le bot"),
        ("list", "Voir les produits suivis"),
        ("delete", "Supprimer un produit"),
        ("help", "Afficher l'aide"),
    ],
    "de": [
        ("start", "Bot starten"),
        ("list", "Verfolgte Produkte anzeigen"),
        ("delete", "Produkt löschen"),
        ("help", "Hilfe anzeigen"),
    ],
    "id": [
        ("start", "Mulai bot"),
        ("list", "Lihat produk yang dilacak"),
        ("delete", "Hapus produk"),
        ("help", "Tampilkan bantuan"),
    ],
    "tr": [
        ("start", "Botu başlat"),
        ("list", "Takip edilen ürünleri gör"),
        ("delete", "Ürünü sil"),
        ("help", "Yardımı göster"),
    ],
}

# ── Setup function ───────────────────────────────────────────

LANGUAGES = list(BOT_NAMES.keys())


async def setup_bot_metadata(bot: Bot) -> None:
    """Set localised bot name, description, and commands via Telegram API."""

    # Set default (English, no language_code)
    try:
        await bot.set_my_name(BOT_NAMES["en"])
        await bot.set_my_description(BOT_DESCRIPTIONS["en"])
        await bot.set_my_short_description(BOT_SHORT_DESCRIPTIONS["en"])
        await bot.set_my_commands(
            [BotCommand(cmd, desc) for cmd, desc in BOT_COMMANDS["en"]]
        )
        logger.info("Set default (en) bot metadata")
    except Exception as e:
        logger.error(f"Failed to set default bot metadata: {e}")

    # Set per-language overrides
    for lang in LANGUAGES:
        if lang == "en":
            continue  # already set as default
        try:
            await bot.set_my_name(BOT_NAMES[lang], language_code=lang)
            await bot.set_my_description(BOT_DESCRIPTIONS[lang], language_code=lang)
            await bot.set_my_short_description(
                BOT_SHORT_DESCRIPTIONS[lang], language_code=lang
            )
            await bot.set_my_commands(
                [BotCommand(cmd, desc) for cmd, desc in BOT_COMMANDS[lang]],
                language_code=lang,
            )
            logger.info(f"Set bot metadata for '{lang}'")
        except Exception as e:
            logger.error(f"Failed to set bot metadata for '{lang}': {e}")
