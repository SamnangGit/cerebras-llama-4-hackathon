from apscheduler.schedulers.asyncio import AsyncIOScheduler
import yaml
from typing import Optional
from controllers.analysis_controller import AnalysisController

class ReportScheduler:
    def __init__(self, telegram_bot):
        self.telegram_bot = telegram_bot
        self.file_path = "public/uploads/prompts/prompt.yaml"
        self.analysis_controller = AnalysisController()
        self.scheduler: Optional[AsyncIOScheduler] = None

    async def send_scheduled_report(self) -> None:
        """Generate and send scheduled report based on predefined prompt"""
        try:
            with open(self.file_path, "r") as f:
                prompts = yaml.load(f, Loader=yaml.FullLoader)
                
            sql_prompt = prompts["Analyse_prompt"]
            chart_type = prompts["Chart_type"]
            html_prompt = f"Based on this data, generate a html page for me to visualize it as a {chart_type}"
            
            print(f"Generating report with SQL prompt: {sql_prompt}")
            print(f"HTML prompt: {html_prompt}")
            
            html_file_path, explanation = self.analysis_controller.retrive_and_generate_html_file(
                sql_prompt=sql_prompt,
                html_prompt=html_prompt
            )
            
            await self.telegram_bot.send_html_file(
                file_path=html_file_path,
                explanation=explanation
            )
            
        except Exception as e:
            print(f"Error generating report: {str(e)}")

    def start_scheduler(self) -> None:
        """Initialize and start the scheduler based on yaml configuration"""
        try:
            with open(self.file_path, "r") as f:
                prompts = yaml.load(f, Loader=yaml.FullLoader)
                
            interval_type = prompts["Interval"].lower()
            self.scheduler = AsyncIOScheduler()
            
            job_config = {
                'hour': 9,
                'minute': 0,
                'func': self.send_scheduled_report
            }
            
            if interval_type == "weekly":
                self.scheduler.add_job(
                    **job_config,
                    trigger='cron',
                    day_of_week='mon'  # Monday
                )
            else:  # monthly or default
                self.scheduler.add_job(
                    **job_config,
                    trigger='cron',
                    day='last'  # Last day of the month
                )
                
            self.scheduler.start()
            print(f"Scheduler started. Reports will be sent {interval_type} at 9:00 AM")
            
        except Exception as e:
            print(f"Error starting scheduler: {str(e)}")

    async def stop_scheduler(self) -> None:
        """Stop the scheduler gracefully"""
        if self.scheduler and self.scheduler.running:
            self.scheduler.shutdown()
            print("Scheduler stopped")