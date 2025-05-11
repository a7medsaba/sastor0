from bot.auth import AuthHandlers

class OfferHandlers:
    @staticmethod
    def start_offer(update, context):
        """بدء عملية إضافة عرض جديد"""
        if not AuthHandlers.check_registration(update.message.from_user.id):
            update.message.reply_text("⚠️ يرجى التسجيل أولاً باستخدام الأمر /register")
            return

        user_id = str(update.message.from_user.id)
        users = Database.load_data('users')
        user = users.get(user_id)
        
        context.user_data['offer'] = {
            'user_id': user_id,
            'user_name': user['name'],
            'user_phone': user['phone'],
            'status': 'pending',
            'files': []
        }
        
        update.message.reply_text(
            "📦 يرجى إرسال تفاصيل العرض:\n"
            "العنوان\nالوصف\nالسعر\nالعملة (اختياري)"
        )