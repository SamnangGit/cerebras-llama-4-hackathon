from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import os
from dotenv import load_dotenv
from controllers.analysis_controller import AnalysisController
from typing import List, Dict, Optional

class TelegramBot:
    def __init__(self):
        load_dotenv()
        
        # Initialize controllers
        self.analysis_controller = AnalysisController()
        
        # Configure paths
        self.IMG_DIR = "public/uploads/images"
        self.LOG_DIR = "public/uploads/logs"
        self.PROMPT_DIR = "public/uploads/prompts"
        self._create_directories()
        
        # Bot configuration
        self.TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
        self.PHOTO_AUTHORIZED_CHATS = [int(os.getenv("CAR_GROUP_CHAT_ID"))]
        self.TEXT_AUTHORIZED_CHATS = [int(os.getenv("ADMIN_GROUP_CHAT_ID"))]
        self.FILE_AUTHORIZED_CHATS = [int(os.getenv("PERSONAL_CHAT_ID"))]
        
        # Initialize application
        self.app: Optional[Application] = None

    def _create_directories(self) -> None:
        """Create necessary directories if they don't exist"""
        for directory in [self.IMG_DIR, self.LOG_DIR, self.PROMPT_DIR]:
            os.makedirs(directory, exist_ok=True)

    def _log_message(self, log_entry: str, log_file_name: str) -> None:
        """Log message to specified file"""
        log_file_path = os.path.join(self.LOG_DIR, log_file_name)
        with open(log_file_path, "a", encoding="utf-8") as log_file:
            log_file.write(f"\n{log_entry}\n{'='*50}")

    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle incoming photos in the photo group"""
        chat_id = update.effective_chat.id
        if chat_id not in self.PHOTO_AUTHORIZED_CHATS:
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
            file_path = os.path.join(self.IMG_DIR, file_name)
            await photo_file.download_to_drive(file_path)
            
            result = self.analysis_controller.extract_and_save_fuel_transaction(file_path, image_info)
            
            log_entry = (
                f"Image Details:\n"
                f"- Saved as: {file_name}\n"
                f"- Sent by: {user_full_name}\n"
                f"- Username: @{username}\n"
                f"- User ID: {user.id}\n"
                f"- Chat ID: {chat_id}"
            )
            self._log_message(log_entry, "image_logs.txt")

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

    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle incoming text messages in the text group"""
        chat_id = update.effective_chat.id
        if chat_id not in self.TEXT_AUTHORIZED_CHATS:
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

        try:
            html_prompt = "Based on this data, generate a html page for me to visualize it."
            html_file_path, explanation = self.analysis_controller.retrive_and_generate_html_file(
                sql_prompt=message, 
                html_prompt=html_prompt
            )
            print(html_file_path)
            if html_file_path == "RESTRICTED":
                await update.message.reply_text(explanation)
                return
            
            with open(html_file_path, "rb") as html_file:
                await update.message.reply_document(document=html_file)
            await update.message.reply_text(explanation)

            log_entry = (
                f"Text Message Details:\n"
                f"- Message: {message}\n"
                f"- Sent by: {user_full_name}\n"
                f"- Username: @{username}\n"
                f"- User ID: {user.id}\n"
                f"- Chat ID: {chat_id}"
            )
            self._log_message(log_entry, "text_logs.txt")

        except Exception as e:
            await update.message.reply_text(f"❌ Failed to process message: {str(e)}")

    async def handle_file(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle incoming files in the file chat"""
        try:
            chat_id = update.effective_chat.id
            if str(chat_id) not in [str(id) for id in self.FILE_AUTHORIZED_CHATS]:
                print(f"Unauthorized file message from chat ID: {chat_id}")
                await update.message.reply_text("This chat is not authorized for file uploads.")
                return

            file = update.message.document
            file_name = file.file_name
            file_path = os.path.join(self.PROMPT_DIR, file_name)
            
            file_obj = await file.get_file()
            await file_obj.download_to_drive(file_path)
            
            await update.message.reply_text(f"File saved successfully: {file_name}")
        except Exception as e:
            print(f"Error in handle_file: {str(e)}")
            try:
                await update.message.reply_text(f"❌ Failed to save file: {str(e)}")
            except Exception as reply_error:
                print(f"Failed to send error message: {str(reply_error)}")

    async def send_html_file(self, file_path: str, explanation: str) -> None:
        """Send HTML file and explanation to text group"""
        try:
            bot = Bot(token=self.TOKEN)
            chat_id = self.TEXT_AUTHORIZED_CHATS[0]
            
            with open(file_path, "rb") as html_file:
                await bot.send_document(
                    chat_id=chat_id,
                    document=html_file,
                    filename=os.path.basename(file_path),
                    read_timeout=60,
                    write_timeout=60,
                    connect_timeout=60,
                    pool_timeout=60
                )
            
            await bot.send_message(
                chat_id=chat_id,
                text=explanation,
                read_timeout=30,
                write_timeout=30,
                connect_timeout=30,
                pool_timeout=30
            )
        except Exception as e:
            print(f"Error sending file to Telegram: {str(e)}")

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command"""
        chat_id = update.effective_chat.id
        if chat_id in self.PHOTO_AUTHORIZED_CHATS:
            await update.message.reply_text('Bot is running! Send an image to save it.')
        elif chat_id in self.TEXT_AUTHORIZED_CHATS:
            await update.message.reply_text('Bot is running! Send a text message to save it.')
        else:
            await update.message.reply_text('This bot is not authorized for this chat.')

    async def init_bot(self) -> None:
        """Initialize the telegram bot"""
        try:
            self.app = Application.builder().token(self.TOKEN).build()
            
            # Add handlers
            self.app.add_handler(CommandHandler("start", self.start_command))
            
            photo_filter = filters.PHOTO & filters.Chat(chat_id=self.PHOTO_AUTHORIZED_CHATS)
            self.app.add_handler(MessageHandler(photo_filter, self.handle_photo))
            
            text_filter = filters.TEXT & ~filters.COMMAND & filters.Chat(chat_id=self.TEXT_AUTHORIZED_CHATS)
            self.app.add_handler(MessageHandler(text_filter, self.handle_text))
            
            file_filter = filters.Document.ALL & filters.Chat(chat_id=self.FILE_AUTHORIZED_CHATS)
            self.app.add_handler(MessageHandler(file_filter, self.handle_file))
            
            # Initialize the bot
            await self.app.initialize()
            await self.app.start()
            
            print(f"Starting Telegram bot...")
            print(f"Monitoring photo messages in these chats: {self.PHOTO_AUTHORIZED_CHATS}")
            print(f"Monitoring text messages in these chats: {self.TEXT_AUTHORIZED_CHATS}")
            print(f"Monitoring file messages in these chats: {self.FILE_AUTHORIZED_CHATS}")
            
        except Exception as e:
            print(f"Error initializing bot: {e}")
            raise

    async def stop_bot(self) -> None:
        """Stop the telegram bot"""
        if self.app:
            try:
                if self.app.updater and self.app.updater.running:
                    await self.app.updater.stop()
                if self.app.running:
                    await self.app.stop()
                await self.app.shutdown()
            except Exception as e:
                print(f"Error during bot shutdown: {e}")

    def get_status(self) -> Dict:
        """Get current bot status"""
        return {
            "bot_running": self.app is not None and self.app.is_running,
            "photo_monitored_chats": self.PHOTO_AUTHORIZED_CHATS,
            "text_monitored_chats": self.TEXT_AUTHORIZED_CHATS,
            "file_monitored_chats": self.FILE_AUTHORIZED_CHATS
        }