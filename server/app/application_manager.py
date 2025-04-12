from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio
from utils.telegram_bot import TelegramBot
from commands.report_scheduler import ReportScheduler
from configs.cors import configure_cors
from middlewares.api_logger import setup_logging_middleware
from routers.api import router

class ApplicationManager:
    def __init__(self):
        self.telegram_bot = TelegramBot()
        self.report_scheduler = None
        self.bot_task = None
        
    def configure_app(self, app: FastAPI) -> None:
        """Configure FastAPI application with middleware and routes"""
        setup_logging_middleware(app)
        configure_cors(app)
        app.include_router(router)
        
        # Add bot status endpoint
        @app.get("/bot/status")
        async def bot_status():
            return self.telegram_bot.get_status()
        
    @asynccontextmanager
    async def lifespan(self, app: FastAPI):
        """Manage the lifecycle of the application"""
        print("Starting application lifecycle...")
        
        # Initialize the bot first
        await self.telegram_bot.init_bot()
        print("Bot initialized...")
        
        # Start bot polling in a separate task
        self.bot_task = asyncio.create_task(
            self.telegram_bot.app.updater.start_polling()
        )
        print("Bot polling started...")
        
        # Initialize and start the scheduler
        # self.report_scheduler = ReportScheduler(self.telegram_bot)
        # self.report_scheduler.start_scheduler()
        # print("Scheduler started...")
        
        try:
            yield
        finally:
            print("Shutting down application...")
            try:
                # Stop the scheduler
                if self.report_scheduler:
                    await self.report_scheduler.stop_scheduler()
                    print("Scheduler stopped")
                
                # Stop the bot
                if self.telegram_bot:
                    await self.telegram_bot.stop_bot()
                    print("Bot stopped")
                
                # Cancel polling task if it's still running
                if self.bot_task and not self.bot_task.done():
                    self.bot_task.cancel()
                    try:
                        await self.bot_task
                    except (asyncio.CancelledError, RuntimeError):
                        pass
                    print("Bot task cancelled")
                    
            except Exception as e:
                print(f"Error during application shutdown: {e}")

    def create_application(self) -> FastAPI:
        """Create and configure a new FastAPI application"""
        app = FastAPI(lifespan=self.lifespan)
        self.configure_app(app)
        return app