import json
import shutil
from pathlib import Path
from datetime import datetime
from .config import FILE_PATHS

class Database:
    @staticmethod
    def load_data(file_key):
        """تحميل بيانات JSON مع التعامل مع الأخطاء"""
        try:
            with open(FILE_PATHS[file_key], 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # إرجاع هيكل بيانات افتراضي بناءً على نوع الملف
            if file_key in ['users', 'favorites']:
                return {}
            return []

    @staticmethod
    def save_data(file_key, data):
        """حفظ البيانات في ملف JSON مع التعامل الآمن"""
        try:
            with open(FILE_PATHS[file_key], 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving data: {e}")
            return False

    @staticmethod
    def get_next_id(items):
        """إنشاء ID فريد"""
        if not items:
            return 1
        if isinstance(items, dict):
            return max(int(k) for k in items.keys()) + 1
        return max(item.get('id', 0) for item in items) + 1

    @staticmethod
    def get_user(user_id):
        """استرجاع بيانات مستخدم"""
        users = Database.load_data('users')
        return users.get(str(user_id))

    @staticmethod
    def register_user(user_data):
        """تسجيل مستخدم جديد"""
        users = Database.load_data('users')
        users[str(user_data['user_id'])] = user_data
        return Database.save_data('users', users)

        
    @staticmethod
    def backup_data():
        """إنشاء نسخة احتياطية من البيانات"""
        backup_dir = Path("data/backups")
        backup_dir.mkdir(exist_ok=True)
        for file in FILE_PATHS.values():
            shutil.copy2(file, backup_dir / f"{file.stem}_{datetime.now().strftime('%Y%m%d')}.json")
