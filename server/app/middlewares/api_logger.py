from starlette.concurrency import iterate_in_threadpool
from starlette.requests import Request
import time
from datetime import datetime
import os

def setup_logging_middleware(app):
    async def middleware(request: Request, call_next):
        try:
            req_body = await request.json()
        except Exception:
            req_body = None

        start_time = time.perf_counter()
        response = await call_next(request)
        process_time = time.perf_counter() - start_time

        res_body = [section async for section in response.body_iterator]
        response.body_iterator = iterate_in_threadpool(iter(res_body))

        # Create logs directory if it doesn't exist
        if not os.path.exists("logs"):
            os.makedirs("logs")

        # Stringified response body object
        res_body_str = res_body[0].decode()
        
        # Get current timestamp
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Save to log file
        with open("logs/api.log", "a") as log_file:
            log_file.write(
                f"[{current_time}]\n"
                f"Request Body: {req_body}\n"
                f"Response Status Code: {response.status_code}\n"
                f"Response Body: {res_body_str}\n"
                f"Processing Time: {process_time:.4f} seconds\n"
                f"-------------------------\n"
            )

        return response

    app.middleware("http")(middleware)