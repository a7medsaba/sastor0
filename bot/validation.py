import re
from datetime import datetime

class Validator:
    @staticmethod
    def validate_phone(phone):
        """التحقق من صحة رقم الهاتف"""
        pattern = r'^\+?[0-9]{10,15}$'
        return re.match(pattern, phone) is not None

    @staticmethod
    def validate_email(email):
        """التحقق من صحة الإيميل"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    @staticmethod
    def validate_date(date_str):
        """التحقق من صحة التاريخ"""
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False