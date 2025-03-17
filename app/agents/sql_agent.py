from langchain_core.messages import HumanMessage, SystemMessage
from agents.schemas.sql_query import SQLQuery
from agents.schemas.html_text import HTMLText
from agents.schemas.sematic_table import SemanticTable
from agents.model import GenerativeModel
import base64
from datetime import datetime
from agents.prompt_templates import generate_html_text_prompt, generate_psql_query_prompt, get_text_from_image_prompt, generate_mysql_query_prompt

class SQLAgent:
    def __init__(self):
        pass


    def generate_struture_output_from_image(self, prompt: str, image_path: str, model: GenerativeModel, schema: any) -> str:
        try:
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode("utf-8")
            messages = get_text_from_image_prompt(prompt, image_data)
            llm = model.with_structured_output(schema)
            response = llm.invoke([messages])
            return response

        except Exception as e:
            raise Exception(f"Error generating text: {str(e)}")
            

    def generate_sql_query(self, schema: str, prompt: str, model: GenerativeModel) -> str:
        try:
            current_date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            llm = model.with_structured_output(SQLQuery)
            messages = generate_psql_query_prompt(prompt, schema, current_date_time)
            # messages = generate_mysql_query_prompt(prompt, schema, current_date_time)
            system_message = messages[0]
            human_message = messages[1]
            print(human_message)
            response = llm.invoke([system_message, human_message])
            return response
        except Exception as e:
            raise Exception(f"Error generating SQL query: {str(e)}")
        
        

    def generate_html_text(self, prompt: str, data: str, model: GenerativeModel) -> HTMLText:
        try:
            llm = model.with_structured_output(HTMLText)
            messages = generate_html_text_prompt(prompt, data)
            system_message = messages[0]
            human_message = messages[1]
            # print(human_message)
            # print(system_message)
            response = llm.invoke([system_message, human_message])
            return response
        except Exception as e:
            raise Exception(f"Error generating HTML text: {str(e)}")
        

    def get_main_table_from_prompt(self, prompt: str, relational_tables: str, model: GenerativeModel) -> str:
        try:
            llm = model.with_structured_output(SemanticTable)
            messages = HumanMessage(content=f"Based on the following prompt: {prompt} give me the main table name and their related table based on the following relational tables: {relational_tables}")
            response = llm.invoke([messages])
            return response.table_names
        except Exception as e:
            raise Exception(f"Error getting main table from prompt: {str(e)}")
        
