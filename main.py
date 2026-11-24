
import os
import re
from urllib.parse import urlparse
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

TOKEN = os.getenv("BOT_TOKEN")

def check_site(url):
    if not re.match(r"^https?://", url, re.I):
        url = "https://" + url

    try:
        parsed = urlparse(url)
        host = parsed.hostname

        if not host or "." not in host:
            return "❌ ভুল ওয়েবসাইট লিংক।"

        warnings = []

        if parsed.scheme != "https":
            warnings.append("HTTPS নেই")

        if "@" in parsed.netloc:
            warnings.append("লিংকে সন্দেহজনক @ চিহ্ন আছে")

        if host.startswith("xn--") or ".xn--" in host:
            warnings.append("বিশেষ Unicode ডোমেইন")

        if re.match(r"^\d{1,3}(\.\d{1,3}){3}$", host):
            warnings.append("ডোমেইনে IP address ব্যবহার করা হয়েছে")

        shorteners = [
            "bit.ly", "tinyurl.com", "t.co",
            "cutt.ly", "shorturl.at"
        ]

        if any(host == s or host.endswith("." + s) for s in shorteners):
            warnings.append("লিংকটি URL shortener")

        if warnings:
            return (
                "⚠️ সতর্কতা: সন্দেহজনক বৈশিষ্ট্য পাওয়া গেছে\n\n"
                + "\n".join("• " + w for w in warnings)
                + "\n\nএটি প্রতারণার নিশ্চিত প্রমাণ নয়।"
            )

        return (
            "✅ প্রাথমিক পরীক্ষা সম্পন্ন।\n"
            "বড় কোনো সাধারণ URL সতর্কতা পাওয়া যায়নি।\n\n"
            "এটি সাইট নিরাপদ হওয়ার নিশ্চয়তা নয়।"
        )

    except Exception:
        return "❌ লিংক পরীক্ষা করা যায়নি।"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛡️ Gaming Site Checker Bot\n\n"
        "যেকোনো ওয়েবসাইটের লিংক পাঠান।\n"
        "আমি প্রাথমিক নিরাপত্তা পরীক্ষা করব।"
    )

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    result = check_site(url)

    await update.message.reply_text(
        "🔍 Site Check Report\n\n" + result
    )

def main():
    if not TOKEN:
        raise ValueError("BOT_TOKEN সেট করা হয়নি")

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link)
    )

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
          
