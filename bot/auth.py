from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from telegram.ext import ConversationHandler
from bot.database import Database
from datetime import datetime

GET_NAME, GET_PHONE = range(2)

class AuthHandlers:
    @staticmethod
    async def start_registration(update, context):
        """بدء عملية التسجيل"""
        if Database.get_user(update.message.from_user.id):
            await update.message.reply_text("⚠️ أنت مسجل بالفعل!")
            return ConversationHandler.END
            
        await update.message.reply_text(
            "👋 مرحباً! يرجى إدخال اسمك الكامل:",
            reply_markup=ReplyKeyboardRemove()
        )
        return GET_NAME

    @staticmethod
    async def get_name(update, context):
        """حفظ الاسم"""
        context.user_data['registration'] = {
            'user_id': update.message.from_user.id,
            'name': update.message.text,
            'username': update.message.from_user.username
        }
        
        await update.message.reply_text(
            "📱 يرجى إرسال رقم هاتفك أو استخدام الزر أدناه:",
            reply_markup=ReplyKeyboardMarkup(
                [[KeyboardButton("مشاركة رقم الهاتف", request_contact=True)]],
                resize_keyboard=True,
                one_time_keyboard=True
            )
        )
        return GET_PHONE

    @staticmethod
    async def get_phone(update, context):
        """حفظ رقم الهاتف"""
        if update.message.contact:
            phone = update.message.contact.phone_number
        else:
            phone = update.message.text

        user_data = {
            **context.user_data['registration'],
            'phone': phone,
            'registration_date': datetime.now().isoformat(),
            'last_active': datetime.now().isoformat()
        }

        Database.register_user(user_data)
        await update.message.reply_text(
            "✅ تم تسجيل بياناتك بنجاح!",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END

    @staticmethod
    def check_registration(user_id):
        """التحقق من تسجيل المستخدم"""
        return bool(Database.get_user(user_id))