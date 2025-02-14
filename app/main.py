from fastapi import FastAPI
import uvicorn
from configs.cors import configure_cors
from routers.api import router
import os
from dotenv import load_dotenv
from middlewares.api_logger import setup_logging_middleware

load_dotenv(override=True)


app = FastAPI()
setup_logging_middleware(app)
configure_cors(app)

app.include_router(router)


if __name__ == "__main__":
    if os.getenv("APP_ENV") == "local":
        uvicorn.run(app, host="127.0.0.1", port=8000) 
    else:
        uvicorn.run(app, host="0.0.0.0", port=7000) 
