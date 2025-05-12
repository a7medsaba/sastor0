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
from fastapi import FastAPI
from threading import Thread

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

# المتغيرات البيئية
BOT_TOKEN = os.environ['BOT_TOKEN']
WEBHOOK_URL = os.environ['WEBHOOK_URL']
PORT = int(os.environ.get('PORT', 8443))

# حل عربي مستقر: تعطيل Healthcheck نهائيًا (الأفضل لـ Railway)
# يمكنك حذف هذا الجزء إذا أردت تفعيله لاحقًا
health_app = FastAPI()

@health_app.get("/health")
def health_check():
    return {"status": "ok", "bot": "running"}

def run_health_check():
    import uvicorn
    uvicorn.run(health_app, host="0.0.0.0", port=8000)

# تشغيل Healthcheck في خيط منفصل (اختياري)
# Thread(target=run_health_check, daemon=True).start()



async def main():
    # إعداد صلاحيات المجلدات
    os.system(f"chmod -R 775 {os.path.join(os.path.dirname(__file__), '../data')}")
    
    # إنشاء تطبيق البوت
    app = Application.builder().token(BOT_TOKEN).build()
    await setup_handlers(app)
    
    # طباعة معلومات التشغيل
    webhook_url = f"{WEBHOOK_URL}/{BOT_TOKEN}"
    print(f"🌐 عنوان الويب هوك: {webhook_url}")
    print(f"🔄 جاري ضبط الويب هوك على البورت {PORT}...")
    
    try:
        # 1. احذف أي ويب هوك قديم
        await app.bot.delete_webhook()
        await asyncio.sleep(1)
        
        # 2. اضبط الويب هوك الجديد
        await app.bot.set_webhook(
            url=webhook_url,
            drop_pending_updates=True,
            allowed_updates=["message", "callback_query"]
        )
        print("✅ تم ضبط الويب هوك بنجاح!")
        
        # 3. تشغيل الويب هوك
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
