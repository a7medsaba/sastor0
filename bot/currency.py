from bot.config import DEFAULT_CURRENCY, CURRENCY_RATES

class CurrencyConverter:
    @staticmethod
    def convert(amount, from_currency, to_currency=DEFAULT_CURRENCY):
        """تحويل العملات مع التعامل مع أنواع البيانات"""
        try:
            amount = float(amount)
            if from_currency.upper() == to_currency.upper():
                return amount
            
            rate = CURRENCY_RATES.get(from_currency.upper(), 1)
            return round(amount * rate, 2)
        except (ValueError, TypeError):
            return 0.0

    @staticmethod
    def format_price(amount, currency):
        """تنسيق السعر مع رمز العملة مع تحسين العرض"""
        symbols = {
            "SAR": "﷼",
            "USD": "$",
            "EUR": "€",
            "GBP": "£"
        }
        try:
            formatted_amount = "{:,.2f}".format(float(amount))
        except (ValueError, TypeError):
            formatted_amount = "0.00"
            
        return f"{symbols.get(currency.upper(), currency)} {formatted_amount}"