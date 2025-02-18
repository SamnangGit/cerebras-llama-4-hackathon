from apscheduler.schedulers.asyncio import AsyncIOScheduler
from controllers.ocr_controller import OCRController
from utils.telegram import send_html_file


sql_prompt = [
    "I want to get the total quantity of fuel based on product type",
]

html_prompt = [
    "Based on this data, generate a html page for me to visualize it as a bar chart",
]

# handle generating report based on pre-define prompt
async def send_scheduled_report():
    try:
        ocr_controller = OCRController()
        html_file_path, explanation = ocr_controller.retrive_and_generate_html_file(sql_prompt=sql_prompt[0], html_prompt=html_prompt[0])
        await send_html_file(file_path=html_file_path, explanation=explanation)
    except Exception as e:
        print(f"Error generating report: {str(e)}")

def schedule_report_sender():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        send_scheduled_report,
        'cron',
        day_of_week='monday',  # 0-6 or mon,tue,wed,thu,fri,sat,sun
        hour=9,               # 24 hour format
        minute=0              # Minute of the hour
    )

    # scheduler.add_job(send_scheduled_report, 'interval', minutes=1)
    
    scheduler.start()
    print("Scheduler started. Weekly reports will be sent every Monday at 9:00 AM")


