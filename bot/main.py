from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    CallbackQueryHandler
)
from telegram import version as TG_VER
import os
import asyncio
from fastapi import FastAPI
from threading import Thread
import uvicorn

# التحقق من توافق إصدار مكتبة telegram
try:
    from telegram import version_info
except ImportError:
    version_info = (0, 0, 0, 0, 0)

if version_info < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"هذا الكود غير متوافق مع الإصدار {TG_VER} الحالي. يلزم الإصدار 20.x أو أعلى"
    )

from bot.auth import AuthHandlers, GET_NAME, GET_PHONE
from bot.user import UserHandlers
from bot.admin import AdminHandlers
from bot.offers import OfferHandlers

# المتغيرات البيئية
BOT_TOKEN = os.environ['BOT_TOKEN']
WEBHOOK_URL = os.environ['WEBHOOK_URL']
PORT = int(os.environ.get('PORT', 8443))

# إعداد تطبيق FastAPI للـ Healthcheck
health_app = FastAPI()

@health_app.get("/health")
def health_check():
    return {"status": "ok", "bot": "running"}

def run_health_check():
    health_port = int(os.environ.get("HEALTH_PORT", 8000))
    uvicorn.run(health_app, host="0.0.0.0", port=health_port)

# تشغيل Healthcheck في خيط منفصل
Thread(target=run_health_check, daemon=True).start()

async def setup_handlers(app):
    # إضافة معالجات التسجيل
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

    # أوامر المستخدمين
    app.add_handler(CommandHandler('start', UserHandlers.start))
    app.add_handler(CallbackQueryHandler(UserHandlers.handle_callbacks))

    # نظام العروض
    app.add_handler(CommandHandler('offer', OfferHandlers.start_offer))
    app.add_handler(MessageHandler(filters.PHOTO, OfferHandlers.handle_files))

async def main():
    # إعداد صلاحيات المجلد
    os.system(f"chmod -R 775 {os.path.join(os.path.dirname(__file__), '../data')}")

    # إنشاء التطبيق
    app = Application.builder().token(BOT_TOKEN).build()
    await setup_handlers(app)

    # طباعة معلومات الويب هوك
    webhook_url = f"{WEBHOOK_URL}/{BOT_TOKEN}"
    print(f"🌐 عنوان الويب هوك: {webhook_url}")
    print(f"🔄 جاري ضبط الويب هوك على البورت {PORT}...")

    try:
        await app.bot.delete_webhook()
        await asyncio.sleep(1)

        await app.bot.set_webhook(
            url=webhook_url,
            drop_pending_updates=True,
            allowed_updates=["message", "callback_query"]
        )
        print("✅ تم ضبط الويب هوك بنجاح!")

        await app.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=BOT_TOKEN,
            webhook_url=webhook_url
        )
    except Exception as e:
        print(f"❌ فشل تشغيل البوت: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
