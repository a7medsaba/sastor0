from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import asyncio
import os

BOT_TOKEN = os.environ['BOT_TOKEN']

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

class Registration(StatesGroup):
    get_name = State()
    get_phone = State()

@dp.message_handler(commands=['register'])
async def start_registration(message: types.Message):
    await message.answer("يرجى إدخال اسمك:")
    await Registration.get_name.set()

@dp.message_handler(state=Registration.get_name)
async def get_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("يرجى إرسال رقم هاتفك أو كتابته:")
    await Registration.get_phone.set()

@dp.message_handler(content_types=['contact', 'text'], state=Registration.get_phone)
async def get_phone(message: types.Message, state: FSMContext):
    phone = message.contact.phone_number if message.contact else message.text
    await state.update_data(phone=phone)
    data = await state.get_data()
    await message.answer(f"تم التسجيل!\nالاسم: {data['name']}\nالهاتف: {data['phone']}")
    await state.finish()

async def main():
    print("✅ بدء تشغيل البوت عبر Aiogram...")
    await dp.start_polling()

if __name__ == "__main__":
    asyncio.run(main())
