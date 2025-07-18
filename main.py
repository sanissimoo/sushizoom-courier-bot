import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
import os

API_TOKEN = os.getenv("BOT_TOKEN")
GROUP_CHAT_ID = os.getenv("CHAT_ID")  # має виглядати як -1001234567890

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

class Form(StatesGroup):
    waiting_for_address = State()

# Кнопки для кур'єра
main_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
main_keyboard.add(
    KeyboardButton("🚗 Прийняв доставку"),
    KeyboardButton("⏱️ Затримуюсь")
).add(
    KeyboardButton("📍 Прибув"),
    KeyboardButton("✅ Завершив доставку")
)

@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    await message.answer("Оберіть дію:", reply_markup=main_keyboard)

@dp.message_handler(lambda message: message.text == "🚗 Прийняв доставку")
async def process_start_delivery(message: types.Message):
    await message.answer("Введіть адресу доставки:")
    await Form.waiting_for_address.set()

@dp.message_handler(state=Form.waiting_for_address)
async def process_address(message: types.Message, state: FSMContext):
    user = message.from_user
    username = user.username or user.first_name or "Кур'єр"
    address = message.text

    msg = f"🚗 Кур'єр @{username} прийняв доставку.\n📍 Адреса: {address}"
    try:
        await bot.send_message(chat_id=GROUP_CHAT_ID, text=msg)
    except Exception as e:
        await message.answer("Помилка надсилання до групи. Повідомте адміністратора.")
        logging.error(f"Error sending message to group: {e}")

    # Видаляємо адресу з чату кур'єра
    try:
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    except:
        pass

    await state.finish()
    await message.answer("✅ Адресу прийнято. Оберіть наступну дію:", reply_markup=main_keyboard)

@dp.message_handler(lambda message: message.text == "⏱️ Затримуюсь")
async def delay_handler(message: types.Message):
    username = message.from_user.username or message.from_user.first_name or "Кур'єр"
    msg = f"⏱️ @{username} повідомив(ла), що затримується."
    await bot.send_message(chat_id=GROUP_CHAT_ID, text=msg)
    await message.answer("Затримка зафіксована.", reply_markup=main_keyboard)

@dp.message_handler(lambda message: message.text == "📍 Прибув")
async def arrived_handler(message: types.Message):
    username = message.from_user.username or message.from_user.first_name or "Кур'єр"
    msg = f"📍 @{username} прибув на адресу."
    await bot.send_message(chat_id=GROUP_CHAT_ID, text=msg)
    await message.answer("Прибуття зафіксовано.", reply_markup=main_keyboard)

@dp.message_handler(lambda message: message.text == "✅ Завершив доставку")
async def complete_handler(message: types.Message):
    username = message.from_user.username or message.from_user.first_name or "Кур'єр"
    msg = f"✅ @{username} завершив доставку."
    await bot.send_message(chat_id=GROUP_CHAT_ID, text=msg)
    await message.answer("Доставку завершено.", reply_markup=main_keyboard)

if __name__ == '__main__':
    import requests

    # Тестове повідомлення після запуску
    try:
        BOT_TOKEN = os.getenv("BOT_TOKEN")
        CHAT_ID = os.getenv("CHAT_ID")
        TEXT = "✅ Тестове повідомлення: бот запущено і намагається писати в групу."

        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": TEXT}
        response = requests.post(url, data=payload)
        print("Відповідь Telegram:", response.json())
    except Exception as e:
        print("Помилка при надсиланні тестового повідомлення:", e)

    executor.start_polling(dp, skip_updates=True)

