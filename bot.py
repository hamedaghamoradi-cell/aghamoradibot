import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# --- خواندن اطلاعات از فایل JSON ---
with open("bot_data.json", "r", encoding="utf-8") as f:
    bot_data = json.load(f)

# --- ساخت دکمه‌ها ---
def make_buttons(buttons):
    keyboard = []
    for btn in buttons:
        if "command" in btn:
            keyboard.append([InlineKeyboardButton(btn["text"], callback_data=btn["command"])])
        elif "url" in btn:
            keyboard.append([InlineKeyboardButton(btn["text"], url=btn["url"])])
    return InlineKeyboardMarkup(keyboard)

# --- پاسخ به دستورات مستقیم (مثلاً /start) ---
async def handle_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    for cmd in bot_data["commands"]:
        if cmd["command"] == user_text:
            buttons = make_buttons(cmd.get("buttons", []))
            photo = cmd.get("photo")
            if photo:
                await update.message.reply_photo(photo=photo, caption=cmd["response"], reply_markup=buttons)
            else:
                await update.message.reply_text(cmd["response"], reply_markup=buttons)
            return

    await update.message.reply_text("❗دستور ناشناخته است. لطفاً از منوی ربات استفاده کنید.")

# --- پاسخ به دکمه‌های داخلی (callback data) ---
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    for cmd in bot_data["commands"]:
        if cmd["command"] == query.data:
            buttons = make_buttons(cmd.get("buttons", []))
            photo = cmd.get("photo")

            if photo:
                await query.edit_message_media(
                    media=InputMediaPhoto(media=photo, caption=cmd["response"]),
                    reply_markup=buttons
                )
            else:
                await query.edit_message_text(cmd["response"], reply_markup=buttons)
            return

# --- اجرای ربات ---
if __name__ == "__main__":
    TOKEN = ""
    app = ApplicationBuilder().token(TOKEN).build()

    # افزودن همه دستورها
    for cmd in bot_data["commands"]:
        command_name = cmd["command"].replace("/", "")
        app.add_handler(CommandHandler(command_name, handle_command))

    app.add_handler(CallbackQueryHandler(handle_callback))

    print("✅ ربات با موفقیت اجرا شد. حالا در تلگرام /start را بفرست.")
    app.run_polling()

