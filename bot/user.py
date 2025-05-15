from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from .database import Database
from .currency import CurrencyConverter

class UserHandlers:
    @staticmethod
    async def start(update, context):
        """الواجهة الرئيسية للمستخدم"""
        user = Database.get_user(update.message.from_user.id)
        if not user:
            await update.message.reply_text("👋 مرحباً! يرجى التسجيل أولاً باستخدام /register")
            return

        keyboard = [
            [InlineKeyboardButton("🛒 تصفح المنتجات", callback_data="browse_products")],
            [InlineKeyboardButton("⭐ المفضلة", callback_data="my_favorites")],
            [InlineKeyboardButton("📦 عروضي", callback_data="my_offers")],
            [InlineKeyboardButton("📊 طلباتي", callback_data="my_orders")]
        ]
        await update.message.reply_text(
            f"مرحباً {user['name']}! 👋\nاختر من القائمة:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    @staticmethod
    async def handle_callbacks(update, context):
        """معالجة جميع callback queries"""
        query = update.callback_query
        await query.answer()

        if query.data == "browse_products":
            await UserHandlers.browse_products(update, context)
        elif query.data == "my_favorites":
            await UserHandlers.view_favorites(update, context)
        # يمكنك إضافة المزيد من معالجات الـ callbacks هنا

    @staticmethod
    async def browse_products(update, context):
        """تصفح المنتجات"""
        query = update.callback_query
        products = Database.load_data('products')
        
        keyboard = []
        for product in products[:10]:  # عرض أول 10 منتجات
            btn = InlineKeyboardButton(
                f"{product['name']} - {product['price']} {product.get('currency', 'SAR')}",
                callback_data=f"view_product_{product['id']}")
            keyboard.append([btn])
        
        if len(products) > 10:
            keyboard.append([InlineKeyboardButton("التالي →", callback_data="page_2")])
        
        await query.edit_message_text(
            "🛍 المنتجات المتاحة:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    @staticmethod
    async def view_favorites(update, context):
        """عرض المفضلة"""
        query = update.callback_query
        user_id = update.effective_user.id
        favorites = Database.load_data('favorites').get(str(user_id), [])
        products = Database.load_data('products')
        
        fav_products = [p for p in products if p['id'] in favorites]
        
        if not fav_products:
            await query.edit_message_text("⭐ لم تقم بإضافة أي منتجات إلى المفضلة بعد")
            return

        keyboard = []
        for product in fav_products:
            keyboard.append([
                InlineKeyboardButton(
                    product['name'],
                    callback_data=f"view_product_{product['id']}")
            ])
        
        await query.edit_message_text(
            "⭐ منتجاتك المفضلة:",
            reply_markup=InlineKeyboardMarkup(keyboard))
