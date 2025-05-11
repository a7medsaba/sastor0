from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackQueryHandler
from bot.auth import AuthHandlers, GET_NAME, GET_PHONE
from bot.user import UserHandlers
from bot.admin import AdminHandlers
from bot.offers import OfferHandlers
from bot.config import BOT_TOKEN
import os
from pathlib import Path
import asyncio
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
   # app.add_handler(MessageHandler(filters.PHOTO | filters.ATTACHMENT, OfferHandlers.handle_files))
app.add_handler(MessageHandler(filters.PHOTO | filters.Document.ALL, OfferHandlers.handle_files))
    # أوامر المسؤول
    app.add_handler(CommandHandler('admin', AdminHandlers.admin_panel))
 # ============= إدارة العملات =============
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
    os.system(f"chmod -R 777 {os.path.join(os.path.dirname(__file__), '../data')}")
# os.system(f"chmod -R 775 {os.path.join(os.path.dirname(__file__), '../data')}")
    # إنشاء التطبيق مع الإصدار الجديد
    app = Application.builder().token(BOT_TOKEN).build()
    
    await setup_handlers(app)
    
    # بدء البوت
  # إضافة هذه السطر للتأكد من تشغيل البوت
    print("✅ البوت يعمل الآن!")
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
