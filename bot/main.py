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

# التحقق من توافق إصدار مكتبة telegram
try:
    from telegram import version_info
except ImportError:
    version_info = (0, 0, 0, 0, 0)

if version_info < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"هذا الكود غير متوافق مع الإصدار {TG_VER} الحالي. يلزم الإصدار 20.x أو أعلى"
    )

# ✅ تعديل المسارات لتناسب مجلد bot/
from .auth import AuthHandlers, GET_NAME, GET_PHONE
from .user import UserHandlers
from .admin import AdminHandlers
from .offers import OfferHandlers

# المتغيرات البيئية
BOT_TOKEN = os.environ['BOT_TOKEN']
ADMIN_USER_ID = int(os.environ['ADMIN_USER_ID'])  # مثال على استخدامه لاحقًا

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

    app.add_handler(CommandHandler('start', UserHandlers.start))
    app.add_handler(CallbackQueryHandler(UserHandlers.handle_callbacks))

    app.add_handler(CommandHandler('offer', OfferHandlers.start_offer))
    app.add_handler(MessageHandler(filters.PHOTO, OfferHandlers.handle_files))

async def main():
    os.system(f"chmod -R 775 {os.path.join(os.path.dirname(__file__), '../data')}")
    app = Application.builder().token(BOT_TOKEN).build()
    await setup_handlers(app)

    print("✅ يتم الآن تشغيل البوت عبر Long Polling...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
