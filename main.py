import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes,
    ConversationHandler, filters
)
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_CHAT_ID = int(os.getenv("CHAT_ID"))

CHOOSING, TYPING_ADDRESS = range(2)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

keyboard = ReplyKeyboardMarkup(
    [
        ["🚗 Прийняв доставку", "⏱ Затримуюсь"],
        ["📍 Прибув", "✅ Завершив доставку"]
    ],
    resize_keyboard=True
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.delete()
    await update.effective_chat.send_message("Оберіть дію:", reply_markup=keyboard)
    return CHOOSING

async def handle_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text
    await update.message.delete()

    if text == "🚗 Прийняв доставку":
        await update.effective_chat.send_message("Введіть адресу доставки:", reply_markup=ReplyKeyboardRemove())
        return TYPING_ADDRESS

    if text == "⏱ Затримуюсь":
        message_text = "⏱ Кур'єр затримується"
    elif text == "📍 Прибув":
        message_text = "📍 Кур'єр прибув на адресу"
    elif text == "✅ Завершив доставку":
        message_text = "✅ Доставка завершена"
    else:
        return CHOOSING

    full_message = f"{message_text}\nКур'єр: @{user.username or user.first_name}"
    await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=full_message)
    return CHOOSING

async def handle_address(update: Update, co_
