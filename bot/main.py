import os
import asyncio
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    filters, ConversationHandler, CallbackQueryHandler
)
from bot.auth import AuthHandlers, GET_NAME, GET_PHONE
from bot.user import UserHandlers
from bot.offers import OfferHandlers
from threading import Thread
import uvicorn

# المتغيرات
BOT_TOKEN = os.environ['BOT_TOKEN']
WEBHOOK_URL = os.environ['WEBHOOK_URL']
PORT = int(os.environ.get("PORT", 8443))

# FastAPI
app_fastapi = FastAPI()
telegram_app = None  # سيُملأ لاحقًا

@app_fastapi.get("/health")
def health_check():
    return {"status": "ok"}

@app_fastapi.post(f"/{BOT_TOKEN}")
async def telegram_webhook(request: Request):
    data = await request.json()
    await telegram_app.update_queue.put(data)
    return JSONResponse(content={"ok": True})

# إعداد البوت
async def setup_handlers(app):
    conv = ConversationHandler(
        entry_points=[CommandHandler("register", AuthHandlers.start_registration)],
        states={
            GET_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, AuthHandlers.get_name)],
            GET_PHONE: [
                MessageHandler(filters.CONTACT, AuthHandlers.get_phone),
                MessageHandler(filters.TEXT & ~filters.COMMAND, AuthHandlers.get_phone)
            ],
        },
        fallbacks=[],
    )
    app.add_handler(conv)
    app.add_handler(CommandHandler("start", UserHandlers.start))
    app.add_handler(CallbackQueryHandler(UserHandlers.handle_callbacks))
    app.add_handler(CommandHandler("offer", OfferHandlers.start_offer))
    app.add_handler(MessageHandler(filters.PHOTO, OfferHandlers.handle_files))

async def start_bot():
    global telegram_app
    telegram_app = Application.builder().token(BOT_TOKEN).build()
    await setup_handlers(telegram_app)

    webhook_url = f"{WEBHOOK_URL}/{BOT_TOKEN}"
    await telegram_app.bot.delete_webhook()
    await asyncio.sleep(1)
    await telegram_app.bot.set_webhook(
        url=webhook_url,
        drop_pending_updates=True,
        allowed_updates=["message", "callback_query"]
    )

    await telegram_app.initialize()
    await telegram_app.start()
    print("✅ البوت شغّال!")

# دمج FastAPI + Telegram
if __name__ == "__main__":
    # تشغيل FastAPI في ثريد
    Thread(target=lambda: uvicorn.run(app_fastapi, host="0.0.0.0", port=PORT), daemon=True).start()
    # تشغيل البوت
    asyncio.run(start_bot())
