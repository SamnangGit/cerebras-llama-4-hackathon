import uvicorn
import os
from dotenv import load_dotenv
from application_manager import ApplicationManager

# from utils.db_ops import DBOps

# db_ops = DBOps()
# db_ops.init_db()

load_dotenv(override=True)

# Create the application manager instance
app_manager = ApplicationManager()

# Create and configure the FastAPI application
app = app_manager.create_application()

if __name__ == "__main__":
    if os.getenv("APP_ENV") == "local":
        uvicorn.run(app, host="127.0.0.1", port=8000)
    else:
        uvicorn.run(app, host="0.0.0.0", port=7001)