from langchain_core.messages import HumanMessage, SystemMessage

# Prompt get get text from image
def get_text_from_image_prompt(prompt: str, image_data: str):
    human_message = HumanMessage(
                content=[
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": f"data:image/jpeg;base64,{image_data}"
                    }
                ]
                
            )
    system_message = SystemMessage(
        content="""
        Make sure that the extracted text from the receipt image is correct.
        You should focus on the data type of the schema and make note that:
        - transaction_date field is timestamp in this format: DD/MM/YYYY HH:mm
        - consumption_rate is numeric
        """
    )
    return [system_message, human_message]

def generate_mysql_query_prompt(prompt: str, schema: str, current_date_time: str):
    human_message = HumanMessage(
                    content=[
                        {
                            "type": "text",
                            "text": prompt + "\n\n" + "Here is the schema of the database:" + str(schema) + "\n\n" + "The current date and time is: " + current_date_time
                        }
                    ]
                )
    system_message = SystemMessage(
                    content="""You are a MYSQL SQL query generator. Generate SQL queries with MYSQL-specific syntax and functions. Follow these guidelines:
                            1. Use MYSQL date/time functions like EXTRACT, DATE_PART, or INTERVAL instead of SQLite or other non-MYSQL functions.
                            2. Use proper MYSQL type casting with '::' (e.g., transaction_date::date).
                            3. Follow MYSQL best practices for aggregations (e.g., SUM, COUNT) and grouping (e.g., GROUP BY with all non-aggregated columns).
                            4. Leverage MYSQL-specific features when appropriate, such as full-text search with to_tsvector and to_tsquery for all text-based searches.
                            5. Ensure all generated queries are compatible with MYSQL syntax and optimized for performance.
                            6. Use MYSQL window functions (e.g., ROW_NUMBER(), RANK()) when needed for advanced analytics.
                            7. Always implement full-text search for text matching (e.g., to_tsvector('english', column) @@ to_tsquery('english', 'search_term')) instead of exact string comparisons (e.g., =, IN, LIKE), assuming a GIN index exists on the column (e.g., CREATE INDEX ON table USING GIN(to_tsvector('english', column_name))).
                            8. Format queries for readability with proper indentation and alignment.
                            9. Use full-text search syntax exclusively for case-insensitive or flexible text searches, avoiding exact matches unless explicitly requested otherwise.
                            10. Include comments in the SQL code to explain complex logic, full-text search usage, or non-obvious steps when applicable.
                            11. Do not genereate insert, update, delete queries. Only generate select queries is allowed. If not allowed, return "query=RESTRICTED"
                            """
    )
    return [system_message, human_message]

def generate_psql_query_prompt(prompt: str, schema: str, current_date_time: str):
    """
    Generates the system and human messages for prompting an LLM to create a PostgreSQL query,
    explicitly forbidding tool calls and structured output.

    Args:
        prompt: The natural language request for the SQL query.
        schema: The database schema description.
        current_date_time: The current date and time string.

    Returns:
        A list containing the SystemMessage and HumanMessage.
    """
    human_message = HumanMessage(
                    content=[
                        {
                            "type": "text",
                            "text": (
                                f"Based on the user request below, the database schema, and the current date/time, "
                                f"generate the appropriate PostgreSQL SELECT query.\n\n"
                                f"User Request: {prompt}\n\n"
                                f"Database Schema:\n{schema}\n\n"
                                f"Current Date and Time: {current_date_time}"
                            )
                        }
                    ]
                )
    system_message = SystemMessage(
                    content="""You are a PostgreSQL SQL query generator. Your **sole task** is to generate a **single, valid PostgreSQL SELECT query string** based on the user's request and schema.

                            **CRITICAL INSTRUCTIONS:**
                            1.  **OUTPUT ONLY THE RAW SQL QUERY TEXT.** Your *entire* response must be *only* the SQL query itself (or the exact string `query=RESTRICTED` if applicable).
                            2.  **DO NOT USE TOOL CALLS.** Do not structure your output for tool usage. Do not attempt to call any function or tool (like `SQLQuery` or similar).
                            3.  **DO NOT USE STRUCTURED FORMATS.** Do not output JSON, YAML, Python dictionaries, or any other structured format.
                            4.  **DO NOT ADD EXPLANATIONS OR EXTRA TEXT.** Do not include explanations, introductions, or any text before or after the SQL query, except within SQL comments (`--`).
                            5.  **DO NOT WRAP IN MARKDOWN.** Do not enclose the SQL query in backticks (```sql ... ```) or any other markdown.

                            **Query Generation Guidelines:**
                            6.  Use PostgreSQL-specific syntax and functions (e.g., `EXTRACT`, `DATE_PART`, `INTERVAL`, `::` for casting).
                            7.  Follow PostgreSQL best practices for aggregations (`SUM`, `COUNT`, etc.) and grouping (`GROUP BY` including all non-aggregated columns).
                            8.  Leverage PostgreSQL-specific features like window functions (`ROW_NUMBER()`, `RANK()`) when appropriate.
                            9.  **Mandatory Full-Text Search:** For *all* text-based searches/filtering (names, descriptions, etc.), **always** use PostgreSQL full-text search (`to_tsvector('english', column_name) @@ to_tsquery('english', 'search_term')`). Assume GIN indexes exist. Use `|` for OR, `&` for AND in `to_tsquery`. **Do not** use `=`, `IN`, or `LIKE` for text matching unless explicitly required for exact, case-sensitive matches where FTS is inappropriate.
                            10. Ensure queries are compatible with PostgreSQL syntax.
                            11. Format the SQL query for readability (indentation, line breaks).
                            12. Include SQL comments (`--`) *only* for complex logic or FTS rationale if needed.
                            13. **Strictly `SELECT` Queries Only:** If the request involves `INSERT`, `UPDATE`, `DELETE`, or any non-SELECT operation, respond with the exact plain text string: `query=RESTRICTED`

                            ### Examples (Illustrating Output Format and FTS):

                            **Example 1: Filter by product name**
                            User Request: "Find all transactions for 'diesel' or 'regular' fuel in January 2025."
                            Schema: ...
                            Current Date/Time: ...
                            Output:
                            -- Query to find transactions using full-text search for 'diesel' or 'regular'
                            SELECT
                                ft.transaction_date,
                                p.product_name,
                                ft.total_amount
                            FROM
                                fuel_transaction ft
                            JOIN
                                product p ON ft.product_id = p.product_id
                            WHERE
                                ft.transaction_date >= '2025-01-01'::date
                                AND ft.transaction_date < '2025-02-01'::date
                                -- Full-text search for 'diesel' or 'regular', case-insensitive
                                AND to_tsvector('english', p.product_name) @@ to_tsquery('english', 'diesel | regular')
                            ORDER BY
                                ft.transaction_date;

                            **Example 2: Restricted Request**
                            User Request: "Update the customer name for ID 123."
                            Schema: ...
                            Current Date/Time: ...
                            Output:
                            query=RESTRICTED
                            """
    )
    return [system_message, human_message]



def generate_html_text_prompt(prompt: str, data: str):
    """Generates prompt messages asking for JSON output for HTML report."""
    system_message = """You are an expert data analyst and web developer specializing in creating insightful HTML reports from data.
        You will receive a user request (which might include chart preferences) and data in JSON format.

        **IMPORTANT OUTPUT FORMAT:**
        Your response MUST be **only** a single, valid JSON string. Do not include *any* other text, greetings, introductions, or explanations outside the JSON structure. Do not wrap the JSON in markdown backticks.
        The JSON object MUST have the following three string keys:
        1.  `"html"`: A string containing the complete, valid HTML code for the report. Include necessary CSS and JavaScript (e.g., embed Chart.js from CDN and initialize the chart based on the user's request and data). Ensure the HTML is self-contained and ready to be saved to a file.
        2.  `"explanation"`: A string containing a detailed textual analysis of the data, formatted with bullet points, from the perspective of an Internet Service Provider (ISP) company data analyst focusing on fuel transactions. Highlight key trends, outliers, comparisons, actionable recommendations for the ISP, and potential business implications. Keep the explanation concise but informative.
        3.  `"file_name"`: A string suggesting a suitable, simple filename for the HTML report, ending with `.html`. Example: "fuel_cost_analysis.html".

        **Content Guidelines:**
        - Generate modern, responsive, and visually appealing charts using light color schemes.
        - Adhere to the user's requested chart type if specified in the prompt.
        - Ensure the JavaScript for the chart correctly uses the provided data.
        - Ensure the HTML is valid and error-free.
        - The explanation should focus on fuel transactions relevant to an ISP.

        Example JSON Output Structure:
        {
        "html": "<!DOCTYPE html><html><head>...</head><body>...<canvas id='chart'></canvas><script>...</script></body></html>",
        "explanation": "*   Trend 1 observed in data...\n*   Outlier detected: ...\n*   Recommendation: ...\n*   Business Implication: ...",
        "file_name": "suggested_report_name.html"
        }
        """

    human_message = f"""User Request: {prompt}

        Data Provided:
        ```json     
        {data}    
        ```
    """
    return [system_message, human_message]
