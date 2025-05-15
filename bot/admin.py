from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from .database import Database
from .config import ADMIN_USER_ID, CURRENCY_RATES, DATA_DIR 

class AdminHandlers:
    # ... (الأساليب السابقة تبقى كما هي)
    @staticmethod
    async def backup_data(update, context):
        """نسخ احتياطي للبيانات"""
        if str(update.effective_user.id) != ADMIN_USER_ID:
            return
            
        backup_path = DATA_DIR / "backups"
        backup_path.mkdir(exist_ok=True)
        
    @staticmethod
    async def manage_currencies(update, context):
        """إدارة أسعار العملات (دالة غير متزامنة)"""
        query = update.callback_query
        await query.answer()
        
        current_rates = Database.load_data('currencies').get('rates', CURRENCY_RATES)
        
        text = "💱 <b>إدارة أسعار العملات</b>\n\n"
        for currency, rate in current_rates.items():
            text += f"{currency}: 1 = {rate} SAR\n"
        
        keyboard = [
            [InlineKeyboardButton("🔄 تحديث سعر", callback_data="update_currency_rate")],
            [InlineKeyboardButton("➕ إضافة عملة", callback_data="add_new_currency")],
            [InlineKeyboardButton("◀️ رجوع", callback_data="admin_main")]
        ]
        
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="HTML"
        )

    @staticmethod
    async def update_currency_rate(update, context):
        """بدء عملية تحديث سعر عملة"""
        query = update.callback_query
        await query.answer()
        
        await query.edit_message_text(
            "↗️ أرسل العملة والسعر الجديد بالشكل:\n\n<code>USD 3.75</code>",
            parse_mode="HTML"
        )
        context.user_data['awaiting_currency_update'] = True

    @staticmethod
    async def handle_currency_update(update, context):
        """معالجة تحديث سعر العملة"""
        if not context.user_data.get('awaiting_currency_update'):
            return
            
        try:
            text = update.message.text.split()
            currency = text[0].upper()
            new_rate = float(text[1])
            
            currencies = Database.load_data('currencies')
            currencies['rates'][currency] = new_rate
            Database.save_data('currencies', currencies)
            
            await update.message.reply_text(f"✅ تم تحديث {currency} إلى {new_rate} SAR")
            
        except (IndexError, ValueError):
            await update.message.reply_text("⚠️ خطأ في التنسيق. استخدم:\n<code>USD 3.75</code>", parse_mode="HTML")
        
        finally:
            context.user_data.pop('awaiting_currency_update', None)

    @staticmethod
    async def add_new_currency(update, context):
        """إضافة عملة جديدة"""
        query = update.callback_query
        await query.answer()
        
        await query.edit_message_text(
            "➕ أرسل العملة وسعرها بالشكل:\n\n<code>GBP 4.95</code>",
            parse_mode="HTML"
        )
        context.user_data['awaiting_new_currency'] = True

    @staticmethod
    async def handle_new_currency(update, context):
        """معالجة إضافة عملة جديدة"""
        if not context.user_data.get('awaiting_new_currency'):
            return
            
        try:
            text = update.message.text.split()
            currency = text[0].upper()
            rate = float(text[1])
            
            currencies = Database.load_data('currencies')
            if currency in currencies['rates']:
                await update.message.reply_text(f"⚠️ العملة {currency} موجودة بالفعل")
            else:
                currencies['rates'][currency] = rate
                Database.save_data('currencies', currencies)
                await update.message.reply_text(f"✅ تمت إضافة {currency} بسعر {rate} SAR")
                
        except (IndexError, ValueError):
            await update.message.reply_text("⚠️ خطأ في التنسيق. استخدم:\n<code>GBP 4.95</code>", parse_mode="HTML")
        
        finally:
            context.user_data.pop('awaiting_new_currency', None)
