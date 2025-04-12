import base64
from datetime import datetime
from typing import Dict, Any, List, Optional
import json
import re 
import traceback 

from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from agents.schemas.sql_query import SQLQuery 
from agents.schemas.html_text import HTMLText 
from agents.schemas.sematic_table import SemanticTable 

from agents.model import GenerativeModel
from agents.prompt_templates import (
    generate_html_text_prompt, 
    generate_psql_query_prompt,
    get_text_from_image_prompt, 
)

class SQLAgent:
    def __init__(self):
        pass

    def generate_struture_output_from_image(self, prompt: str, image_path: str, model: GenerativeModel, schema: Any) -> Any:
        """
        Generates structured output from an image using the provided schema.
        Assumes with_structured_output works for this specific task/schema.
        """
        try:
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode("utf-8")
            messages = get_text_from_image_prompt(prompt, image_data)
            system_message, human_message = messages
            llm = model.with_structured_output(schema)
            response = llm.invoke([system_message, human_message])
            return response
        except Exception as e:
            print(f"Error generating structured output from image: {str(e)}\n{traceback.format_exc()}")
            raise Exception(f"Error generating structured output from image: {str(e)}") from e

    def generate_sql_query(self, schema_str: str, prompt: str, model: GenerativeModel) -> str:
        """
        Generates a raw PostgreSQL query string based on the prompt and schema.
        Handles 'query=RESTRICTED', cleans markdown fences, and ignores leading comments/whitespace.

        Args:
            schema_str: Database schema string.
            prompt: User's natural language request.
            model: GenerativeModel instance.

        Returns:
            Cleaned SQL query string or the exact string "RESTRICTED".
        """
        try:
            current_date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # Use the prompt designed for raw SQL output
            messages = generate_psql_query_prompt(prompt, schema_str, current_date_time)
            system_message, human_message = messages

            print(f"Invoking LLM for raw SQL generation...")
            response_message: AIMessage = model.invoke([system_message, human_message])
            raw_output_from_llm = response_message.content

            print(f"LLM raw response for SQL: ```\n{raw_output_from_llm}\n```") # Log the raw output

            # --- Clean potential markdown fences ---
            cleaned_output = raw_output_from_llm.strip()
            # Regex to find content within ```sql ... ``` or ``` ... ```
            match = re.search(r"```(?:sql)?\s*(.*?)\s*```", cleaned_output, re.DOTALL | re.IGNORECASE)
            if match:
                sql_string_to_validate = match.group(1).strip()
                print(f"Cleaned markdown. SQL Content to validate: ```\n{sql_string_to_validate}\n```")
            else:
                sql_string_to_validate = cleaned_output
                print("No markdown fences found for SQL. Using raw stripped output for validation.")

            # --- Check for RESTRICTED marker ---
            if sql_string_to_validate == "query=RESTRICTED":
                print("SQL generation resulted in RESTRICTED marker.")
                return "RESTRICTED"

            # --- Validate if it's a SELECT query, ignoring comments/whitespace ---
            is_select_query = False
            lines = sql_string_to_validate.splitlines()
            for line in lines:
                stripped_line = line.strip()
                if not stripped_line: continue # Skip empty lines
                if stripped_line.startswith('--'): continue # Skip comment lines
                # Found the first significant line
                if stripped_line.upper().startswith("SELECT"):
                    is_select_query = True
                break # Only check the first significant line

            if not is_select_query:
                 print(f"Warning: Validated LLM output did not start with SELECT after ignoring comments/whitespace. Content: ```\n{sql_string_to_validate}\n```")
                 raise ValueError("LLM response for SQL query was invalid (not SELECT or RESTRICTED after cleaning and comment check).")
            else:
                print("Validated SQL query generated successfully (ignoring comments).")
                # Return the string *including* the comments/original formatting
                return sql_string_to_validate

        except Exception as e:
            print(f"Error generating raw SQL query: {str(e)}\n{traceback.format_exc()}")
            raise Exception(f"Error generating SQL query: {str(e)}") from e


    def generate_html_text(self, prompt: str, data: str, model: GenerativeModel) -> HTMLText:
        """
        Generates HTML report using manual JSON parsing from LLM response.
        Cleans potential markdown fences before parsing. Relies on the prompt
        explicitly asking for JSON output with 'html', 'explanation', 'file_name' keys.

        Args:
            prompt: Prompt guiding report generation (should ask for JSON output).
            data: Data string to be analyzed.
            model: The GenerativeModel instance.

        Returns:
            An HTMLText object containing the html, explanation, and file_name.
        """
        try:
            # Use the prompt that asks for JSON output
            messages = generate_html_text_prompt(prompt, data)
            system_message, human_message = messages
            print(f"Invoking LLM for HTML generation (expecting JSON string)...")

            # Invoke WITHOUT structured output
            response_message: AIMessage = model.invoke([system_message, human_message])
            raw_content = response_message.content
            print(f"LLM raw response content (HTML JSON):\n```\n{raw_content}\n```")

            # --- Robust JSON Cleaning (using regex) ---
            json_string_to_parse = raw_content.strip()
            # Regex to find content within ```json ... ``` or ``` ... ```
            match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", json_string_to_parse, re.DOTALL | re.IGNORECASE)
            if match:
                # If markdown found, use the content inside (the JSON object)
                json_string_to_parse = match.group(1).strip()
                print(f"Cleaned markdown. JSON Content to parse: ```\n{json_string_to_parse}\n```")
            else:
                # Fallback: If no markdown found, check for braces just in case, but prioritize regex
                json_start = json_string_to_parse.find('{')
                json_end = json_string_to_parse.rfind('}')
                if json_start != -1 and json_end != -1:
                    json_string_to_parse = json_string_to_parse[json_start:json_end+1].strip()
                    print("No markdown fences found, but found braces. Extracted content between braces.")
                else:
                    print("No markdown fences or clear braces found. Attempting to parse raw stripped output.")
                    # Use the stripped raw_content directly (json_string_to_parse is already set)

            # --- Parse the cleaned JSON string ---
            try:
                parsed_data = json.loads(json_string_to_parse)
            except json.JSONDecodeError as json_err:
                print(f"Failed to decode JSON from LLM response: {json_err}")
                print(f"Attempted to parse: ```{json_string_to_parse}```")
                # Raise a specific error indicating JSON format failure
                raise Exception(f"LLM response for HTML was not valid JSON after cleaning: {json_err}")

            # --- Validate and instantiate the HTMLText object ---
            try:
                # Use the HTMLText schema defined in context
                html_text_obj = HTMLText(**parsed_data)
                print("Manual JSON parsing and HTMLText validation successful.")
                return html_text_obj
            except Exception as pydantic_err: # Catch Pydantic validation errors specifically
                 print(f"Failed to validate parsed JSON against HTMLText schema: {pydantic_err}")
                 print(f"Parsed data was: {parsed_data}")
                 raise Exception(f"LLM JSON structure did not match expected HTMLText format: {pydantic_err}")

        except Exception as e:
            # Catch any other errors during the process
            print(f"Error during manual HTML generation/parsing: {str(e)}\n{traceback.format_exc()}")
            raise Exception(f"Error generating/processing HTML report structure: {str(e)}") from e

    def get_main_table_from_prompt(self, prompt: str, relational_tables_str: str, model: GenerativeModel) -> List[str]:
        """
        Identifies main and related tables from a prompt and schema info string.
        Assumes with_structured_output works for the SemanticTable schema.
        """
        try:
            llm = model.with_structured_output(SemanticTable) # Uses SemanticTable schema
            prompt_content = (
                f"Analyze the following user prompt and database table relationship information. "
                f"Identify the primary table the user is asking about and any directly related tables necessary to answer the prompt. "
                f"Return ONLY a list of these table names.\n\n"
                f"User Prompt: \"{prompt}\"\n\n"
                f"Database Tables Info:\n{relational_tables_str}"
            )
            messages = [HumanMessage(content=prompt_content)]
            response = llm.invoke(messages) # response is a SemanticTable object
            # Basic validation
            if hasattr(response, 'table_names') and isinstance(response.table_names, list):
                 return response.table_names
            else:
                 print(f"Warning: get_main_table_from_prompt did not return expected structure. Got: {response}")
                 return [] # Return empty list on failure
        except Exception as e:
            print(f"Error getting main table from prompt: {str(e)}\n{traceback.format_exc()}")
            raise Exception(f"Error getting main table from prompt: {str(e)}") from e