from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    CallbackQueryHandler
)
from telegram import __version__ as TG_VER
import os
import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from threading import Thread
import uvicorn

# التحقق من الإصدار
try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(f"الكود غير متوافق مع إصدار {TG_VER}")

# استيراد المعالجات
from bot.auth import AuthHandlers, GET_NAME, GET_PHONE
from bot.user import UserHandlers
from bot.admin import AdminHandlers
from bot.offers import OfferHandlers

# المتغيرات البيئية
BOT_TOKEN = os.environ['BOT_TOKEN']
WEBHOOK_URL = os.environ['WEBHOOK_URL']
PORT = int(os.environ.get('PORT', 8443))

# تطبيق FastAPI الأساسي
app_fastapi = FastAPI()
telegram_app = None  # سيتم تعيينه لاحقًا

@app_fastapi.get("/health")
def health_check():
    return {"status": "ok", "bot": "running"}

@app_fastapi.post(f"/{BOT_TOKEN}")
async def telegram_webhook(req: Request):
    json_data = await req.json()
    await telegram_app.update_queue.put(json_data)
    return JSONResponse(content={"ok": True})

async def setup_handlers(app):
    conv_auth = ConversationHandler(
        entry_points=[CommandHandler('register', AuthHandlers.start_registration)],
        states={
            GET_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, AuthHandlers.get_name)],
            GET_PHONE: [
                MessageHandler(filters.CONTACT, AuthHandlers.get_phone),
                MessageHandler(filters.TEXT & ~filters.COMMAND, AuthHandlers.get_phone)
            ],
        },
        fallbacks=[]
    )
    app.add_handler(conv_auth)

    # المستخدم
    app.add_handler(CommandHandler('start', UserHandlers.start))
    app.add_handler(CallbackQueryHandler(UserHandlers.handle_callbacks))

    # العروض
    app.add_handler(CommandHandler('offer', OfferHandlers.start_offer))
    app.add_handler(MessageHandler(filters.PHOTO, OfferHandlers.handle_files))

async def start_bot():
    global telegram_app

    telegram_app = Application.builder().token(BOT_TOKEN).build()
    await setup_handlers(telegram_app)

    webhook_url = f"{WEBHOOK_URL}/{BOT_TOKEN}"
    print(f"🔗 Webhook URL: {webhook_url}")

    try:
        await telegram_app.bot.delete_webhook()
        await asyncio.sleep(1)
        await telegram_app.bot.set_webhook(
            url=webhook_url,
            drop_pending_updates=True,
            allowed_updates=["message", "callback_query"]
        )
        print("✅ Webhook تم ضبطه بنجاح.")
    except Exception as e:
        print(f"❌ مشكلة في ضبط Webhook: {e}")
        raise

    await telegram_app.start()
    await telegram_app.updater.start_polling()  # نحتاج هذا لتلقي التحديثات

if __name__ == "__main__":
    Thread(target=lambda: uvicorn.run(app_fastapi, host="0.0.0.0", port=PORT), daemon=True).start()
    asyncio.run(start_bot())
