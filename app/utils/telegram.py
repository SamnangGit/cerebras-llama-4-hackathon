from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os
from dotenv import load_dotenv
from controllers.ocr_controller import OCRController

load_dotenv()

ocr_controller = OCRController()

# Telegram Bot Configuration
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
AUTHORIZED_CHATS = [-1002301798755]
SAVE_DIR = "public/uploads"
os.makedirs(SAVE_DIR, exist_ok=True)

# Store the bot application globally
telegram_app = None

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming photos in the group"""
    chat_id = update.effective_chat.id
    if chat_id not in AUTHORIZED_CHATS:
        print(f"Unauthorized message from chat ID: {chat_id}")
        return

    photo = update.message.photo[-1]
    message_id = update.message.message_id
    user = update.message.from_user
    user_full_name = f"{user.first_name} {user.last_name if user.last_name else ''}"
    username = user.username if user.username else "No username"

    try:
        photo_file = await photo.get_file()
        file_name = f"{chat_id}_{message_id}_{username}.jpg"
        file_path = os.path.join(SAVE_DIR, file_name)
        await photo_file.download_to_drive(file_path)
        ocr_controller.extract_and_save_fuel_transaction(file_path)
        log_entry = (
            f"Image Details:\n"
            f"- Saved as: {file_name}\n"
            f"- Sent by: {user_full_name}\n"
            f"- Username: @{username}\n"
            f"- User ID: {user.id}\n"
            f"- Chat ID: {chat_id}"
        )

        log_file_path = os.path.join(SAVE_DIR, "image_logs.txt")
        with open(log_file_path, "a", encoding="utf-8") as log_file:
            log_file.write(f"\n{log_entry}\n{'='*50}")

        await update.message.reply_text(
            f"✅ Image saved successfully!\n"
            f"📤 Uploaded by: {user_full_name} (@{username})"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Failed to save image: {str(e)}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    chat_id = update.effective_chat.id
    if chat_id in AUTHORIZED_CHATS:
        await update.message.reply_text('Bot is running! Send an image to save it.')
    else:
        await update.message.reply_text('This bot is not authorized for this chat.')

async def init_telegram_bot():
    """Initialize the telegram bot without running it"""
    global telegram_app
    telegram_app = Application.builder().token(TOKEN).build()
    telegram_app.add_handler(CommandHandler("start", start))
    telegram_app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    print(f"Starting Telegram bot... Monitoring these chat IDs: {AUTHORIZED_CHATS}")
    return telegram_app

async def stop_telegram_bot():
    """Stop the telegram bot"""
    global telegram_app
    if telegram_app:
        try:
            # First stop the updater
            if telegram_app.updater and telegram_app.updater.running:
                await telegram_app.updater.stop()
            
            # Then stop the application
            if telegram_app.running:
                await telegram_app.stop()
            
            # Finally shutdown the application
            await telegram_app.shutdown()
            
        except Exception as e:
            print(f"Error during bot shutdown: {e}")

def get_bot_status():
    """Get current bot status"""
    return {
        "bot_running": telegram_app is not None and telegram_app.is_running,
        "monitored_chats": AUTHORIZED_CHATS
    }