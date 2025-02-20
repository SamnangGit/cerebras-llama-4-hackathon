from agents.model import GenerativeModel
from agents.schemas.fuel_transaction import FuelTransactionBase
from utils.db_ops import DBOps
from agents.sql_agent import SQLAgent
from agents.tools.file_ops import FileOps
from models.analysis_history import AnalysisHistory
import os

class AnalysisController:
    def __init__(self, model_name: str = "gemini-2.0-flash"):
        """Initialize Analysis controller with specified model."""
        generative_model = GenerativeModel()
        self.model = generative_model.get_model(model_name)
        self.db_ops = DBOps()
        self.sql_agent = SQLAgent()
        self.file_ops = FileOps()
        _, self.SessionLocal = DBOps().get_db()


    def extract_and_save_fuel_transaction(self, image_path: str, image_info: dict) -> FuelTransactionBase:
        """Extract text from image and save fuel transaction"""
        try:
            prompt = (
                "Extract all visible text from this image. "
                "Return only the extracted text, maintaining its original formatting."
            )
            result = self.sql_agent.generate_struture_output_from_image(
                prompt, 
                image_path, 
                self.model, 
                FuelTransactionBase
            )
            self.db_ops.save_fuel_transaction(result, image_info["user_full_name"])
            return result
        except Exception as e:
            raise Exception(f"OCR processing failed: {str(e)}")

    def retrive_and_generate_html_file(self, sql_prompt: str, html_prompt: str) -> str:
        """Generate HTML file based on SQL query results"""
        try:
            schema = self.db_ops.get_schema_info()
            
            sql_query = self.sql_agent.generate_sql_query(schema, sql_prompt, self.model)
            # if html_prompt does not contain chart type, add it
            if "chart" not in html_prompt:
                html_prompt = f" Visualize the data as {html_prompt} {sql_query.chart_type} chart"  
            print(html_prompt)
            result = self.db_ops.execute_sql_query(sql_query.query)
            
            html_file = self.sql_agent.generate_html_text(html_prompt, result, self.model)
            
            file_name = self.file_ops.date_time_now() + "_" + html_file.file_name
            file_path = os.path.join(os.path.dirname(__file__), "..", "public", "reports", file_name)
            self.file_ops.save_html_to_file(html_file.html, file_path)

            analysis_history = AnalysisHistory(
                prompt=sql_prompt,
                file_path=file_path,
                sql_statement=sql_query.query,
                explanation=html_file.explanation
            )
            self.db_ops.save_analysis_history(analysis_history)
            
            return file_path, html_file.explanation
        except Exception as e:
            raise Exception(f"Error generating HTML file: {str(e)}")