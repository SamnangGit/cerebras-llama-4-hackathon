from agents.model import GenerativeModel
from langchain_core.messages import SystemMessage, HumanMessage
class SQLValidator:
    def __init__(self):
        pass

    def correct_sql_statement(self, sql: str, error_message: str, model: GenerativeModel) -> str:
        try:
            system_message = SystemMessage(content="You are a SQL expert. You are given a SQL statement and you need to check if it is correct.")
            human_message = HumanMessage(content=f"The following is the SQL statement: {sql} and the error message is: {error_message}")
            response = model.invoke(system_message, human_message)
            return response
        except Exception as e:
            raise Exception(f"Error validating SQL statement: {str(e)}")