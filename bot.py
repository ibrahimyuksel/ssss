from __future__ import annotations

import os

from dotenv import load_dotenv
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes

from amazon_client import AmazonCredentials, AmazonPaApiClient, AmazonPaApiError

load_dotenv()


def build_client() -> AmazonPaApiClient:
    return AmazonPaApiClient(
        AmazonCredentials(
            access_key=os.environ["AMAZON_ACCESS_KEY"],
            secret_key=os.environ["AMAZON_SECRET_KEY"],
            partner_tag=os.environ["AMAZON_PARTNER_TAG"],
            host=os.getenv("AMAZON_HOST", "webservices.amazon.com"),
            region=os.getenv("AMAZON_REGION", "us-east-1"),
        )
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Merhaba! /fiyat <ürün adı> komutuyla Amazon fiyatlarını resmi API üzerinden çekebilirim."
    )


async def fiyat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("Kullanım: /fiyat kablosuz kulaklık")
        return

    query = " ".join(context.args).strip()
    client = build_client()

    try:
        items = client.search_items(query, marketplace=os.getenv("AMAZON_MARKETPLACE", "www.amazon.com"))
    except KeyError as exc:
        await update.message.reply_text(f"Eksik ortam değişkeni: {exc}")
        return
    except AmazonPaApiError as exc:
        await update.message.reply_text(f"Amazon API hatası: {exc}")
        return

    if not items:
        await update.message.reply_text("Sonuç bulunamadı.")
        return

    lines: list[str] = [f"🔎 *{query}* için sonuçlar:"]
    for idx, item in enumerate(items, start=1):
        lines.append(
            f"\n{idx}. *{item['title']}*\n"
            f"💵 {item['price']}\n"
            f"🔗 {item['url']}"
        )

    await update.message.reply_text("\n".join(lines), parse_mode=ParseMode.MARKDOWN)


def main() -> None:
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("fiyat", fiyat))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
