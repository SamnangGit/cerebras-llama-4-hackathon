from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os
from dotenv import load_dotenv
from controllers.ocr_controller import OCRController

load_dotenv()

ocr_controller = OCRController()

# Telegram Bot Configuration
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
PHOTO_AUTHORIZED_CHATS = [-1002301798755]  # Group for photo processing
TEXT_AUTHORIZED_CHATS = [-1002306963635]   # Replace with your text group ID
FILE_AUTHORIZED_CHATS = [1924007655]
IMG_DIR = "public/uploads/images"
LOG_DIR = "public/uploads/logs"
PROMPT_DIR = "public/uploads/prompts"
os.makedirs(IMG_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(PROMPT_DIR, exist_ok=True)

# Store the bot application globally
telegram_app = None

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming photos in the photo group"""
    chat_id = update.effective_chat.id
    if chat_id not in PHOTO_AUTHORIZED_CHATS:
        print(f"Unauthorized photo message from chat ID: {chat_id}")
        return

    photo = update.message.photo[-1]
    message_id = update.message.message_id
    user = update.message.from_user
    user_full_name = f"{user.first_name} {user.last_name if user.last_name else ''}"
    username = user.username if user.username else "No username"

    image_info = {
        "chat_id": chat_id,
        "message_id": message_id,
        "username": username,
        "user_full_name": user_full_name,
        "user_id": user.id
    }

    try:
        photo_file = await photo.get_file()
        file_name = f"{chat_id}_{message_id}_{username}.jpg"
        file_path = os.path.join(IMG_DIR, file_name)
        await photo_file.download_to_drive(file_path)
        result = ocr_controller.extract_and_save_fuel_transaction(file_path, image_info)
        log_entry = (
            f"Image Details:\n"
            f"- Saved as: {file_name}\n"
            f"- Sent by: {user_full_name}\n"
            f"- Username: @{username}\n"
            f"- User ID: {user.id}\n"
            f"- Chat ID: {chat_id}"
        )

        log_file_path = os.path.join(LOG_DIR, "image_logs.txt")
        with open(log_file_path, "a", encoding="utf-8") as log_file:
            log_file.write(f"\n{log_entry}\n{'='*50}")

        await update.message.reply_text(
            f"✅ Image saved successfully!\n"
            f"📤 Uploaded by: {user_full_name} (@{username})\n"
            f"💰 Fuel Transaction: {result.total_amount} USD\n"
            f"🚗 Vehicle: {result.plate_number}\n"
            f"🏭 Station: {result.station_name}\n"
            f"💸 Product: {result.product_name}\n"
            f"🕒 Date: {result.transaction_date}\n"
            f"💸 Total Amount: {result.total_amount} USD\n"
            f"💸 Quantity: {result.quantity} L\n"
            f"💸 Unit Price: {result.unit_price} USD/L\n"
            f"💸 Previous KM: {result.previous_km}\n"
            f"💸 Actual KM: {result.actual_km}\n"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Failed to save image: {str(e)}")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming text messages in the text group"""
    chat_id = update.effective_chat.id
    if chat_id not in TEXT_AUTHORIZED_CHATS:
        print(f"Unauthorized text message from chat ID: {chat_id}")
        return

    message = update.message.text
    message_id = update.message.message_id
    user = update.message.from_user
    user_full_name = f"{user.first_name} {user.last_name if user.last_name else ''}"
    username = user.username if user.username else "No username"

    message_info = {
        "chat_id": chat_id,
        "message_id": message_id,
        "username": username,
        "user_full_name": user_full_name,
        "user_id": user.id,
        "message": message
    }
    html_prompt = "Based on this data, generate a html page for me to visualize it as a bar chart"

    html_file_path, explanation = ocr_controller.retrive_and_generate_html_file(sql_prompt=message, html_prompt=html_prompt)
    with open(html_file_path, "rb") as html_file:
        await update.message.reply_document(document=html_file)
    await update.message.reply_text(explanation)

    try:
        # Log the text message
        log_entry = (
            f"Text Message Details:\n"
            f"- Message: {message}\n"
            f"- Sent by: {user_full_name}\n"
            f"- Username: @{username}\n"
            f"- User ID: {user.id}\n"
            f"- Chat ID: {chat_id}"
        )

        log_file_path = os.path.join(LOG_DIR, "text_logs.txt")
        with open(log_file_path, "a", encoding="utf-8") as log_file:
            log_file.write(f"\n{log_entry}\n{'='*50}")

    except Exception as e:
        await update.message.reply_text(f"❌ Failed to process message: {str(e)}")

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming files in the file chat"""
    try:
        print(f"Received file from chat ID: {update.effective_chat.id}")
        chat_id = update.effective_chat.id
        
        # Check if chat is in authorized list (convert both to string for comparison)
        if str(chat_id) not in [str(id) for id in FILE_AUTHORIZED_CHATS]:
            print(f"Unauthorized file message from chat ID: {chat_id}")
            await update.message.reply_text("This chat is not authorized for file uploads.")
            return
            
        file = update.message.document
        file_id = file.file_id
        file_name = file.file_name
        file_path = os.path.join(PROMPT_DIR, file_name)
        
        # Get file - this is an awaitable coroutine
        file_obj = await file.get_file()
        await file_obj.download_to_drive(file_path)
        
        await update.message.reply_text(f"File saved successfully: {file_name}")
    except Exception as e:
        print(f"Error in handle_file: {str(e)}")
        try:
            await update.message.reply_text(f"❌ Failed to save file: {str(e)}")
        except Exception as reply_error:
            print(f"Failed to send error message: {str(reply_error)}")




async def send_html_file(file_path: str, explanation: str):
    try:
        bot = Bot(token=TOKEN)
        chat_id = PHOTO_AUTHORIZED_CHATS[0]
        # Send the HTML file with increased timeout (e.g., 60 seconds)
        with open(file_path, "rb") as html_file:
            await bot.send_document(
                chat_id=chat_id,
                document=html_file,
                filename=os.path.basename(file_path),
                read_timeout=60,  # Increase timeout to 60 seconds
                write_timeout=60,  # Increase timeout to 60 seconds
                connect_timeout=60,  # Increase timeout to 60 seconds
                pool_timeout=60  # Increase timeout to 60 seconds
            )
        # Send the explanation with increased timeout
        await bot.send_message(
            chat_id=chat_id,
            text=explanation,
            read_timeout=30,  # Increase timeout to 30 seconds
            write_timeout=30,  # Increase timeout to 30 seconds
            connect_timeout=30,  # Increase timeout to 30 seconds
            pool_timeout=30  # Increase timeout to 30 seconds
        )
    except Exception as e:
        print(f"Error sending file to Telegram: {str(e)}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    chat_id = update.effective_chat.id
    if chat_id in PHOTO_AUTHORIZED_CHATS:
        await update.message.reply_text('Bot is running! Send an image to save it.')
    elif chat_id in TEXT_AUTHORIZED_CHATS:
        await update.message.reply_text('Bot is running! Send a text message to save it.')
    else:
        await update.message.reply_text('This bot is not authorized for this chat.')

async def init_telegram_bot():
    """Initialize the telegram bot without running it"""
    global telegram_app
    telegram_app = Application.builder().token(TOKEN).build()
    
    # Add command handler
    telegram_app.add_handler(CommandHandler("start", start))
    
    # Add photo handler for photo group
    photo_filter = filters.PHOTO & filters.Chat(chat_id=PHOTO_AUTHORIZED_CHATS)
    telegram_app.add_handler(MessageHandler(photo_filter, handle_photo))
    
    # Add text handler for text group
    text_filter = filters.TEXT & ~filters.COMMAND & filters.Chat(chat_id=TEXT_AUTHORIZED_CHATS)
    telegram_app.add_handler(MessageHandler(text_filter, handle_text))
    
    # Add file handler for file chat
    file_filter = filters.Document.ALL & filters.Chat(chat_id=FILE_AUTHORIZED_CHATS)
    telegram_app.add_handler(MessageHandler(file_filter, handle_file))
    
    print(f"Starting Telegram bot...")
    print(f"Monitoring photo messages in these chats: {PHOTO_AUTHORIZED_CHATS}")
    print(f"Monitoring text messages in these chats: {TEXT_AUTHORIZED_CHATS}")
    print(f"Monitoring file messages in these chats: {FILE_AUTHORIZED_CHATS}")
    return telegram_app

async def stop_telegram_bot():
    """Stop the telegram bot"""
    global telegram_app
    if telegram_app:
        try:
            if telegram_app.updater and telegram_app.updater.running:
                await telegram_app.updater.stop()
            if telegram_app.running:
                await telegram_app.stop()
            await telegram_app.shutdown()
        except Exception as e:
            print(f"Error during bot shutdown: {e}")

def get_bot_status():
    """Get current bot status"""
    return {
        "bot_running": telegram_app is not None and telegram_app.is_running,
        "photo_monitored_chats": PHOTO_AUTHORIZED_CHATS,
        "text_monitored_chats": TEXT_AUTHORIZED_CHATS,
        "file_monitored_chats": FILE_AUTHORIZED_CHATS
    }