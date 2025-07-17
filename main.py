from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, CallbackContext
import os

# Змінні середовища
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))  # Наприклад: -1002582699976

# Повідомлення для кнопок
messages = {
    "accept": "🚚 Прийняв доставку",
    "delay": "⏳ Затримуюсь",
    "arrived": "🏦 Прибув",
    "done": "✅ Завершив доставку"
}

# Стан користувача
user_state = {}

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[
        KeyboardButton("Прийняв доставку"),
        KeyboardButton("Затримуюсь")
    ], [
        KeyboardButton("Прибув"),
        KeyboardButton("Завершив доставку")
    ]]

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Оберіть дію:", reply_markup=reply_markup)

# Обробка кнопок і тексту
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.message.from_user.id
    username = update.message.from_user.username or update.message.from_user.first_name

    # Якщо чекаємо адресу після "Прийняв доставку"
    if user_state.get(user_id) == "awaiting_address":
        msg = f"✉️ Кур'єр {username} прийняв доставку
Адреса: {text}"
        await context.bot.send_message(chat_id=CHAT_ID, text=msg)
        user_state[user_id] = None
        await update.message.reply_text("Дякуємо! Адресу передано.")
        return

    # Якщо обрано дію
    for action, label in messages.items():
        if label.endswith(text):
            if action == "accept":
                user_state[user_id] = "awaiting_address"
                await update.message.reply_text("Введіть адресу доставки:")
            else:
                msg = f"✉️ Кур'єр {username} {label}"
                await context.bot.send_message(chat_id=CHAT_ID, text=msg)
                await update.message.reply_text("Ок, оновлено!")
            return

# Запуск бота
if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot is running...")
    app.run_polling()
