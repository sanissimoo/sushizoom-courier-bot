import logging
import os
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes,
    ConversationHandler, filters
)

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

# /start тільки в особистому чаті
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        return
    await update.message.reply_text("Оберіть дію:", reply_markup=keyboard)
    return CHOOSING

# Обробка кнопок
async def handle_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        return
    user = update.effective_user
    text = update.message.text

    if text == "🚗 Прийняв доставку":
        await update.message.reply_text("Введіть адресу доставки:", reply_markup=ReplyKeyboardRemove())
        return TYPING_ADDRESS

    messages = {
        "⏱ Затримуюсь": "⏱ Кур'єр затримується",
        "📍 Прибув": "📍 Кур'єр прибув на адресу",
        "✅ Завершив доставку": "✅ Доставка завершена"
    }

    if text in messages:
        full_message = f"{messages[text]}\nКур'єр: @{user.username or user.first_name}"
        await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=full_message)

    return CHOOSING

# Введення адреси
async def handle_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        return
    user = update.effective_user
    address = update.message.text

    full_message = (
        f"🚗 Кур'єр прийняв доставку\n"
        f"📍 Адреса: {address}\n"
        f"Кур'єр: @{user.username or user.first_name}"
    )
    await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=full_message)
    await update.message.reply_text("Дякую! Оберіть наступну дію:", reply_markup=keyboard)
    return CHOOSING

# /cancel
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        return
    await update.message.reply_text("Скасовано.", reply_markup=keyboard)
    return ConversationHandler.END

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_choice)],
            TYPING_ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_address)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.run_polling()
