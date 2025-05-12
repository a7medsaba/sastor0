import os
import json
from pathlib import Path
from datetime import datetime
#
# إزالة القيم الافتراضية لأسباب أمنية
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_USER_ID = os.getenv("ADMIN_USER_ID")

# مسارات الملفات - باستخدام pathlib للتشغيل على جميع الأنظمة
BASE_DIR = Path(__file__).parent.parent  # الانتقال لمستوى الجذر
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

FILE_PATHS = {
    "users": DATA_DIR / "users.json",
    "categories": DATA_DIR / "categories.json",
    "products": DATA_DIR / "products.json",
    "orders": DATA_DIR / "orders.json",
    "favorites": DATA_DIR / "favorites.json",
    "offers": DATA_DIR / "offers.json",
    "currencies": DATA_DIR / "currencies.json"
}

# تهيئة ملفات JSON إذا لم تكن موجودة
for file_path in FILE_PATHS.values():
    if not file_path.exists():
        with open(file_path, 'w', encoding='utf-8') as f:
            if "users" in file_path.name or "favorites" in file_path.name:
                json.dump({}, f)
            else:
                json.dump([], f)

# إعدادات العملة
DEFAULT_CURRENCY = "SAR"
CURRENCY_RATES = {
    "USD": 3.75,
    "EUR": 4.20,
    "GBP": 4.95
}
# حدود النظام
MAX_PRODUCT_IMAGES = 5
MAX_OFFER_FILES = 3
OFFER_EXPIRY_DAYS = 30  # مدة صلاحية العرض
