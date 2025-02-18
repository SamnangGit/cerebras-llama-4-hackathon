from langchain_core.messages import HumanMessage, SystemMessage
from agents.schemas.sql_query import SQLQuery
from agents.schemas.html_text import HTMLText
from agents.model import GenerativeModel
import base64
from agents.prompt_templates import generate_html_text_promp, generate_sql_query_prompt, get_text_from_image_prompt

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
            llm = model.with_structured_output(SQLQuery)
            messages = generate_sql_query_prompt(prompt, schema)
            system_message = messages[0]
            human_message = messages[1]
            response = llm.invoke([system_message, human_message])
            return response
        except Exception as e:
            raise Exception(f"Error generating SQL query: {str(e)}")
        
        

    def generate_html_text(self, prompt: str, data: str, model: GenerativeModel) -> HTMLText:
        try:
            llm = model.with_structured_output(HTMLText)
            messages = generate_html_text_promp(prompt, data)
            system_message = messages[0]
            human_message = messages[1]
            response = llm.invoke([system_message, human_message])
            return response
        except Exception as e:
            raise Exception(f"Error generating HTML text: {str(e)}")
        


        