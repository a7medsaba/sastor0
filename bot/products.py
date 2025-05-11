from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from bot.database import Database
from bot.currency import CurrencyConverter

class ProductHandlers:
    @staticmethod
    async def show_product(update, context, product_id):
        """عرض تفاصيل المنتج (دالة غير متزامنة)"""
        query = update.callback_query
        await query.answer()
        
        products = Database.load_data('products')
        product = next((p for p in products if p['id'] == product_id), None)
        
        if not product:
            await query.edit_message_text("⚠️ المنتج غير موجود")
            return

        converted_price = CurrencyConverter.convert(
            product['price'],
            product.get('currency', 'SAR')
        )

        text = (
            f"🛍 *{product['name']}*\n\n"
            f"💰 السعر: {CurrencyConverter.format_price(product['price'], product.get('currency', 'SAR'))}\n"
            f"   (~{CurrencyConverter.format_price(converted_price, 'SAR')})\n\n"
            f"📝 الوصف: {product.get('description', 'لا يوجد وصف')}"
        )

        keyboard = [
            [InlineKeyboardButton("🛒 حجز المنتج", callback_data=f"order_{product_id}")],
            [InlineKeyboardButton("⭐ إضافة للمفضلة", callback_data=f"fav_{product_id}")]
        ]
        
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )