from fastapi import FastAPI
import uvicorn
from configs.cors import configure_cors
from routers.api import router
import os
from dotenv import load_dotenv
from middlewares.api_logger import setup_logging_middleware
from contextlib import asynccontextmanager
import asyncio
from utils.telegram import init_telegram_bot, stop_telegram_bot, get_bot_status
from commands.report_scheduler import schedule_report_sender
# from utils.db_ops import DBOps


load_dotenv(override=True)

# db_ops = DBOps()
# db_ops.init_db()

async def start_bot():
    """Start the bot and begin polling"""
    app = await init_telegram_bot()
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    return app

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start the bot when the FastAPI app starts
    bot_task = asyncio.create_task(start_bot())
    
    # Start the scheduler
    schedule_report_sender()
    print("Scheduler started. Weekly reports will be sent every Monday at 9:00 AM")
    
    try:
        yield
    finally:
        # Cleanup when the FastAPI app is shutting down
        try:
            await stop_telegram_bot()
            if not bot_task.done():
                bot_task.cancel()
            try:
                await bot_task
            except (asyncio.CancelledError, RuntimeError):
                pass
        except Exception as e:
            print(f"Error during application shutdown: {e}")

# FastAPI Application
app = FastAPI(lifespan=lifespan)
setup_logging_middleware(app)
configure_cors(app)
app.include_router(router)

# Add an endpoint to check bot status
@app.get("/bot/status")
async def bot_status():
    return get_bot_status()

if __name__ == "__main__":
    if os.getenv("APP_ENV") == "local":
        uvicorn.run(app, host="127.0.0.1", port=8000)
    else:
        uvicorn.run(app, host="0.0.0.0", port=7000)