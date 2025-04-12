import os
import json
import traceback
from typing import Tuple, Optional, Any, Dict, List

from fastapi import HTTPException

from agents.model import GenerativeModel
from utils.db_ops import DBOps
from agents.sql_agent import SQLAgent
from agents.tools.file_ops import FileOps

from agents.schemas.fuel_transaction import FuelTransactionBase 
# from agents.schemas.sql_query import SQLQuery 
from agents.schemas.html_text import HTMLText 
from agents.schemas.sematic_table import SemanticTable 

from models.analysis_history import AnalysisHistory


def format_schema_dict_to_string(schema_data: Any) -> str:
    if isinstance(schema_data, str): return schema_data
    if not isinstance(schema_data, dict): return str(schema_data)
    if not schema_data: return "-- No schema information provided --\n"
    parts = [f"-- Schema for table: {name}\n{defn}\n" for name, defn in schema_data.items()]
    return "\n".join(parts)

def convert_db_result_to_string(data: any) -> str:
    if not data: return "No data returned from query."
    try:
        MAX_ITEMS = 50
        trunc = False
        if isinstance(data, (list, tuple)) and len(data) > MAX_ITEMS:
            data = data[:MAX_ITEMS]
            trunc = True
        json_str = json.dumps(data, indent=2, default=str)
        return json_str + ("\n... (truncated)" if trunc else "")
    except Exception: return str(data)


MAX_SCHEMA_CHARS_IN_PROMPT = 16000 


class AnalysisController:
    def __init__(self, model_name: str = "llama-4-scout-17b-16e-instruct"):
        print(f"Initializing AnalysisController with model: {model_name}")
        generative_model = GenerativeModel()
        self.model = generative_model.get_cerebras_model(model_name)
        self.db_ops = DBOps()
        self.sql_agent = SQLAgent()
        self.file_ops = FileOps()
        try:
            raw_schema = self.db_ops.get_schema_info()
            self.full_db_schema_string = format_schema_dict_to_string(raw_schema)
            print(f"Initialized Full DB Schema (Length: {len(self.full_db_schema_string)} chars). First 500 chars:\n{self.full_db_schema_string[:500]}...")
        except Exception as e:
            print(f"ERROR: Failed to initialize DB schema: {e}")
            self.full_db_schema_string = "-- Error retrieving schema --"
        try:
            self.relationship_info = self.db_ops.get_relationship_tables('table_relationships')
            print(f"Initialized Relationship Info: Status={self.relationship_info.get('status')}")
        except Exception as e:
            print(f"ERROR: Failed to initialize relationship info: {e}")
            self.relationship_info = {"status": False, "data": None, "message": str(e)}

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

    def retrive_and_generate_html_file(self, sql_prompt: str, html_prompt: str) -> Tuple[str, str]:
        """
        Generates SQL (raw), executes it, generates HTML report (via JSON), saves file.
        Includes logic to potentially use relevant schema and truncate if too long.
        """
        print(f"\n--- Starting Analysis ---")
        print(f"Received SQL Prompt: {sql_prompt}")
        print(f"Received HTML Prompt: {html_prompt}")

        current_schema_string_untruncated = self.full_db_schema_string
        schema_source = "Full Schema"
        final_sql_prompt = sql_prompt

        try:
            # 1. Determine Relevant Schema 
            if self.relationship_info.get("status") == True and self.relationship_info.get("data"):
                print("Attempting to identify relevant tables...")
                try:
                    table_names: List[str] = self.sql_agent.get_main_table_from_prompt(
                        sql_prompt, self.relationship_info["data"], self.model
                    )
                    if table_names:
                        print(f"Identified relevant tables: {table_names}")
                        relevant_schema_dict = self.db_ops.get_table_schemas_by_names(table_names)
                        current_schema_string_untruncated = format_schema_dict_to_string(relevant_schema_dict)
                        schema_source = f"Relevant Tables Schema ({', '.join(table_names)})"
                        print(f"Using {schema_source} (Length: {len(current_schema_string_untruncated)} chars).")
                        # Update prompt context
                        final_sql_prompt = (
                                f"{sql_prompt}\n\n---\n"
                                f"Context: Relevant tables are {', '.join(table_names)}. Focus on schema below.\n---\n"
                                f"Generate SQL based on original prompt: '{sql_prompt}'"
                           )
                    else:
                        print("Could not identify relevant tables, using full schema.")
                        schema_source = "Full Schema (Fallback)"
                except Exception as e:
                    print(f"Warning: Failed during relevant table/schema step: {e}. Using full schema.")
                    schema_source = "Full Schema (Error Fallback)"
            else:
                print("No relationship info or status False, using full schema.")

            # --- Schema Truncation ---
            schema_to_pass = current_schema_string_untruncated
            if len(schema_to_pass) > MAX_SCHEMA_CHARS_IN_PROMPT:
                print(f"Warning: Schema length ({len(schema_to_pass)}) exceeds limit ({MAX_SCHEMA_CHARS_IN_PROMPT}). Truncating.")
                schema_to_pass = schema_to_pass[:MAX_SCHEMA_CHARS_IN_PROMPT] + "\n-- SCHEMA TRUNCATED --"
            print(f"Schema to be passed to LLM (Length: {len(schema_to_pass)} chars, Source: {schema_source}).")


            # 2. Generate RAW SQL Query
            print(f"Generating raw SQL query...")
            sql_query_string = self.sql_agent.generate_sql_query(
                schema_to_pass, final_sql_prompt, self.model
            )
            print(f"SQL Agent returned: ```{sql_query_string}```")

            # 3. Handle RESTRICTED Query
            if sql_query_string == "RESTRICTED":
                print("Query identified as RESTRICTED by agent.")
                explanation = "Operation restricted."
                # ... (Save restricted notice HTML) ...
                reports_dir = os.path.join(os.path.dirname(__file__), "..", "public", "reports")
                os.makedirs(reports_dir, exist_ok=True)
                file_name = self.file_ops.date_time_now() + "_restricted.html"
                file_path = os.path.join(reports_dir, file_name)
                restricted_content = f"<html><body><h1>Operation Restricted</h1><p>{explanation}</p></body></html>"
                self.file_ops.save_html_to_file(restricted_content, file_path)
                return file_path, explanation

            print("SQL query generated successfully.")

            # 4. Execute the SQL Query
            print(f"Executing SQL: {sql_query_string}")
            try:
                query_result = self.db_ops.execute_sql_query(sql_query_string)
                print(f"Query execution successful.")
            except Exception as db_error:
                print(f"Database execution error: {db_error}\n{traceback.format_exc()}")
                raise HTTPException(status_code=500, detail=f"Database Error: Failed to execute query. Error: {db_error}")

            # 5. Prepare Data for HTML generation
            data_string = convert_db_result_to_string(query_result)
            final_html_prompt = html_prompt # Use original HTML prompt
            print("Prepared data for HTML generation.")

            # 6. Generate HTML Content (via JSON parsing in Agent)
            print(f"Generating HTML content (requesting JSON)...")
            try:
                # Expecting an HTMLText object from the agent
                html_text_obj: HTMLText = self.sql_agent.generate_html_text(
                    final_html_prompt, data_string, self.model
                )
                print("HTML content generation successful from agent (via JSON).")
            except Exception as html_gen_error:
                 print(f"Error generating/parsing HTML structure: {html_gen_error}\n{traceback.format_exc()}")
                 raise HTTPException(status_code=500, detail=f"Analysis Error: Failed generation/parsing. Error: {html_gen_error}")

            # 7. Save HTML File using data from HTMLText object
            base_file_name_suggested = html_text_obj.file_name
            safe_suffix = "".join(c for c in base_file_name_suggested if c.isalnum() or c in ('-', '_')).rstrip('.')
            if not safe_suffix: safe_suffix = "report"
            if not safe_suffix.endswith(".html"): safe_suffix += ".html"
            base_file_name = self.file_ops.date_time_now() + "_" + safe_suffix
            reports_dir = os.path.join(os.path.dirname(__file__), "..", "public", "reports")
            os.makedirs(reports_dir, exist_ok=True)
            file_path = os.path.join(reports_dir, base_file_name)
            html_content_to_save = html_text_obj.html
            print(f"Saving generated HTML content ({len(html_content_to_save)} bytes) to: {file_path}")
            self.file_ops.save_html_to_file(html_content_to_save, file_path)

            # 8. Prepare Final Explanation
            html_explanation = html_text_obj.explanation
            full_explanation = f"--- Data / Report Explanation ---\n{html_explanation}"

            # 9. Save Analysis History
            # try:
            #     analysis_history = AnalysisHistory(...)
            #     self.db_ops.save_analysis_history(analysis_history)
            # except Exception as history_error: print(f"Warning: Failed history save: {history_error}")

            print(f"--- Analysis Successful --- Report: {file_path}")
            return file_path, full_explanation

        except HTTPException as http_exc:
              print(f"--- Analysis Failed (HTTPException) --- Status: {http_exc.status_code}, Detail: {http_exc.detail}")
              raise http_exc
        except Exception as e:
            print(f"--- Analysis Failed (Unexpected Error) --- Error: {str(e)}\n{traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"Internal server error during analysis: {str(e)}")