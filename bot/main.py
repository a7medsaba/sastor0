from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    CallbackQueryHandler
)
from telegram import __version__ as TG_VER

# التحقق من توافق إصدار المكتبة
try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"هذا الكود غير متوافق مع الإصدار {TG_VER} الحالي. يلزم الإصدار 20.x أو أعلى"
    )

from bot.auth import AuthHandlers, GET_NAME, GET_PHONE
from bot.user import UserHandlers
from bot.admin import AdminHandlers
from bot.offers import OfferHandlers
from bot.config import BOT_TOKEN
import os
from pathlib import Path
import asyncio
from fastapi import FastAPI
from threading import Thread
BOT_TOKEN = os.environ['BOT_TOKEN']  # مطلوب
ADMIN_USER_ID = os.environ.get('ADMIN_USER_ID', '')  # اختياري
WEBHOOK_URL = os.environ['WEBHOOK_URL']  # مطلوب
PORT = int(os.environ.get('PORT', 8443))  # افتراضي 8443
# إنشاء تطبيق فحص الصحة
health_app = FastAPI()

@health_app.get("/health")
def health_check():
    return {"status": "ok", "bot": "running"}

# تشغيل الخادم في خيط منفصل
def run_health_check():
    import uvicorn
    uvicorn.run(health_app, host="0.0.0.0", port=8000)

Thread(target=run_health_check, daemon=True).start()

async def setup_handlers(app):
    # نظام التسجيل
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
    app.add_handler(MessageHandler(filters.PHOTO | filters.DOCUMENT.ALL, OfferHandlers.handle_files))

    # أوامر المسؤول
    app.add_handler(CommandHandler('admin', AdminHandlers.admin_panel))
    
    # إدارة العملات
    app.add_handler(CallbackQueryHandler(
        AdminHandlers.manage_currencies,
        pattern="^manage_currencies$"
    ))
    app.add_handler(CallbackQueryHandler(
        AdminHandlers.update_currency_rate,
        pattern="^update_currency_rate$"
    ))
    app.add_handler(CallbackQueryHandler(
        AdminHandlers.add_new_currency,
        pattern="^add_new_currency$"
    ))
    
    # معالجات الرسائل النصية للعملات
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        AdminHandlers.handle_currency_update
    ))
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        AdminHandlers.handle_new_currency
    ))

async def main():
    os.system(f"chmod -R 775 {os.path.join(os.path.dirname(__file__), '../data')}")
    app = Application.builder().token(BOT_TOKEN).build()
    await setup_handlers(app)
app = Application.builder().token(BOT_TOKEN).build()
    await setup_handlers(app)
    
    print(f"🚀 بدء تشغيل البوت على البورت {PORT}")
    print(f"🌐 عنوان الويب هوك: {WEBHOOK_URL}/{BOT_TOKEN}")
       webhook_url = f"https://sastor0-production.up.railway.app/{BOT_TOKEN}"
    print(f"🔄 جاري ضبط الويب هوك على: {webhook_url}")
    
    await app.bot.set_webhook(
        url=webhook_url,
        drop_pending_updates=True,  # تجاهل الرسائل القديمة
        allowed_updates=["message", "callback_query"]  # قلل أنواع التحديثات إذا لزم الأمر
    )
    
    await app.run_webhook(
        listen="0.0.0.0",
        port=8443,
        url_path=BOT_TOKEN,
        webhook_url=webhook_url
    )
if __name__ == "__main__":
    asyncio.run(main())
