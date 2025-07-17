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

# Постійна reply-клавіатура
keyboard = ReplyKeyboardMarkup(
    [
        ["🚗 Прийняв доставку", "⏱ Затримуюсь"],
        ["📍 Прибув", "✅ Завершив доставку"]
    ],
    resize_keyboard=True
)

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.delete()
    await update.effective_chat.send_message("Оберіть дію:", reply_markup=keyboard)
    return CHOOSING

# Обробка вибору
async def handle_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text
    await update.message.delete()

    if text == "🚗 Прийняв доставку":
        await update.effective_chat.send_message("Введіть адресу доставки:", reply_markup=ReplyKeyboardRemove())
        return TYPING_ADDRESS

    messages = {
        "⏱ Затримуюсь": "⏱ Кур'єр затримується",
        "📍 Прибув": "📍 Кур'єр прибув на адресу",
        "✅ Завершив доставку": "✅ Доставка завершена"
    }

    if text in messages:
        msg = f"{messages[text]}
Кур'єр: @{user.username or user.first_name}"
        await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=msg)
    return CHOOSING

# Прийом адреси
async def handle_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    address = update.message.text
    await update.message.delete()

    msg = (
        f"🚗 Кур'єр прийняв доставку
"
        f"📍 Адреса: {address}
"
        f"Кур'єр: @{user.username or user.first_name}"
    )
    await context.bot.send_message(chat_id=GROUP_CHAT_ID, text=msg)
    await update.effective_chat.send_message("Оберіть дію:", reply_markup=keyboard)
    return CHOOSING

# /cancel
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.delete()
    await update.effective_chat.send_message("Скасовано.", reply_markup=keyboard)
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
