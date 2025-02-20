from apscheduler.schedulers.asyncio import AsyncIOScheduler
from controllers.ocr_controller import OCRController
from utils.telegram import send_html_file
import yaml

file_path = "public/uploads/prompts/prompt.yaml"

# handle generating report based on pre-define prompt
async def send_scheduled_report():
    try:
        with open(file_path, "r") as f:
            prompts = yaml.load(f, Loader=yaml.FullLoader)

        sql_prompt = prompts["Analyse_prompt"]
        chart_type = prompts["Chart_type"]
        html_prompt = f"Based on this data, generate a html page for me to visualize it as a {chart_type}"
        print(sql_prompt)
        print(html_prompt)
        ocr_controller = OCRController()
        html_file_path, explanation = ocr_controller.retrive_and_generate_html_file(sql_prompt=sql_prompt, html_prompt=html_prompt)
        await send_html_file(file_path=html_file_path, explanation=explanation)
    except Exception as e:
        print(f"Error generating report: {str(e)}")

def schedule_report_sender():
    with open(file_path, "r") as f:
        prompts = yaml.load(f, Loader=yaml.FullLoader)
    
    interval_type = prompts["Interval"].lower() 
    scheduler = AsyncIOScheduler()

    if interval_type == "weekly":
        scheduler.add_job(
            send_scheduled_report,
            'cron',
            day_of_week='mon',  # Monday
            hour=9,
            minute=0
        )
    elif interval_type == "monthly":
        scheduler.add_job(
            send_scheduled_report,
            'cron',
            day='last',  # Last day of the month
            hour=9,
            minute=0
        )
    else:
        # return monthly by default
        scheduler.add_job(
            send_scheduled_report,
            'cron',
            day='last',  # Last day of the month
            hour=9,
            minute=0
        )
    scheduler.start()
    print(f"Scheduler started. Reports will be sent {interval_type} at 9:00 AM")