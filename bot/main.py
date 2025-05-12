import os
import asyncio
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters
)

from bot.auth import AuthHandlers, GET_NAME, GET_PHONE
from bot.user import UserHandlers
from bot.admin import AdminHandlers
from bot.offers import OfferHandlers

# قراءة المتغيرات البيئية من إعدادات Railway
BOT_TOKEN = os.environ['BOT_TOKEN']
ADMIN_ID = int(os.environ['ADMIN_USER_ID'])  # تأكد أن القيمة رقم صحيح

async def setup_handlers(app):
    # معالج التسجيل عبر ConversationHandler
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

    # أوامر الأدمن (مثال بسيط)
    app.add_handler(CommandHandler('admin', lambda update, context: update.message.reply_text("أهلاً أيها الأدمن") if update.effective_user.id == ADMIN_ID else None))

    # نظام العروض
    app.add_handler(CommandHandler('offer', OfferHandlers.start_offer))
    app.add_handler(MessageHandler(filters.PHOTO, OfferHandlers.handle_files))

async def main():
    # إعداد صلاحيات المجلد (إن وجد)
    os.system(f"chmod -R 775 {os.path.join(os.path.dirname(__file__), '../data')}")

    # إنشاء التطبيق
    app = Application.builder().token(BOT_TOKEN).build()
    await setup_handlers(app)

    print("✅ يتم الآن تشغيل البوت عبر Long Polling...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
