import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes, ConversationHandler
)
import os

# Змінні середовища
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_CHAT_ID = int(os.getenv("CHAT_ID"))

# Стани для ConversationHandler
CHOOSING, TYPING_ADDRESS = range(2)

# Налаштування логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Кнопки
keyboard = InlineKeyboardMarkup([
    [InlineKeyboardButton("🚗 Прийняв доставку", callback_data="accept")],
    [InlineKeyboardButton("⏱ Затримуюсь", callback_data="delay"),
     InlineKeyboardButton("📍 Прибув", callback_data="arrived")],
    [InlineKeyboardButton("✅ Завершив доставку", callback_data="done")]
])

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Оберіть дію:", reply_markup=keyboard)
    return CHOOSING

# Обробка кнопок
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    action = query.data

    if action == "accept":
        await query.message.reply_text("Будь ласка, введіть адресу доставки:")
        return TYPING_ADDRESS

    messages = {
        "delay": "⏱ Кур'єр затримується",
        "arrived": "📍 Кур'єр прибув на адресу",
        "done": "✅ Доставка завершена"
    }

    if action in messages:
        text = f"{messages[action]}\nКур'єр: @{user.username or user.first_name}"
        await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=text)
        return CHOOSING

# Прийом адреси
async def received_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    address = update.message.text
    text = (
        f"🚗 Кур'єр прийняв доставку\n"
        f"📍 Адреса: {address}\n"
        f"Кур'єр: @{user.username or user.first_name}"
    )
    await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=text)
    await update.message.reply_text("Дякую! Оберіть наступну дію:", reply_markup=keyboard)
    return CHOOSING

# Скасування
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Скасовано.")
    return ConversationHandler.END

# Запуск
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING: [CallbackQueryHandler(button_handler)],
            TYPING_ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, received_address)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.run_polling()
