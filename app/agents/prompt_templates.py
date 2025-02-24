from langchain_core.messages import HumanMessage, SystemMessage


# Prompt get get text from image
def get_text_from_image_prompt(prompt: str, image_data: str):
    message = HumanMessage(
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
    return message

def generate_sql_query_prompt(prompt: str, schema: str):
    human_message = HumanMessage(
                    content=[
                        {
                            "type": "text",
                            "text": prompt + "\n\n" + "Here is the schema of the database:" + str(schema)
                        }
                    ]
                )
    system_message = SystemMessage(
                    content="""You are a PostgreSQL SQL query generator. Generate SQL queries with PostgreSQL-specific syntax and functions. Follow these guidelines:
                            1. Use PostgreSQL date/time functions like EXTRACT, DATE_PART, or INTERVAL instead of SQLite or other non-PostgreSQL functions.
                            2. Use proper PostgreSQL type casting with '::' (e.g., transaction_date::date).
                            3. Follow PostgreSQL best practices for aggregations (e.g., SUM, COUNT) and grouping (e.g., GROUP BY with all non-aggregated columns).
                            4. Leverage PostgreSQL-specific features when appropriate, such as full-text search with to_tsvector and to_tsquery for all text-based searches.
                            5. Ensure all generated queries are compatible with PostgreSQL syntax and optimized for performance.
                            6. Use PostgreSQL window functions (e.g., ROW_NUMBER(), RANK()) when needed for advanced analytics.
                            7. Always implement full-text search for text matching (e.g., to_tsvector('english', column) @@ to_tsquery('english', 'search_term')) instead of exact string comparisons (e.g., =, IN, LIKE), assuming a GIN index exists on the column (e.g., CREATE INDEX ON table USING GIN(to_tsvector('english', column_name))).
                            8. Format queries for readability with proper indentation and alignment.
                            9. Use full-text search syntax exclusively for case-insensitive or flexible text searches, avoiding exact matches unless explicitly requested otherwise.
                            10. Include comments in the SQL code to explain complex logic, full-text search usage, or non-obvious steps when applicable.
                            11. Do not genereate insert, update, delete queries. Only generate select queries is allowed. If not allowed, return "query=RESTRICTED"

                            ### Few-Shot Examples:
                            Below are examples to guide query generation using full-text search as required:

                            **Example 1: Filter by product name**
                            Input: "Find all transactions for 'diesel' or 'regular' fuel in January 2025."
                            Output:
                            ```sql
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
                                ft.transaction_date >= '2025-01-01'
                                AND ft.transaction_date < '2025-02-01'
                                -- Full-text search for 'diesel' or 'regular', case-insensitive
                                AND to_tsvector('english', p.product_name) @@ to_tsquery('english', 'diesel | regular')
                            ORDER BY
                                ft.transaction_date;
                            """
    )
    return [system_message, human_message]


def generate_html_text_prompt(prompt: str, data: str):
    human_message = HumanMessage(
                content=[
                    {
                        "type": "text",
                        "text": prompt + "\n\n" + "Here is the data:" + str(data)
                    }
                ]
            )
    system_message = SystemMessage(
        content=""" 
        You are a helpful assistant that generates HTML code for modern, responsive and visually appealing charts using different light color schemes. Make sure that there is no error in the html code.
        After generating the HTML code, explain the data as an Internet Service Provider company data analyst. Focus on the fuel transaction data that drivers spend on during their work operations. Your explanation should:
        1. Highlight key trends, outliers, or significant comparisons in the fuel transaction data
        2. Explain what the visualization reveals about patterns
        3. Suggest actionable recommendations based on the observed patterns
        4. Point out potential business implications for the ISP company
        5. Make sure the explanation is not too long and not too short
        6. Make sure the explanation is in bullet points

        Important:
        Avoid discussing technical implementation details like responsiveness or design elements.
        Avoid Overrided user requested chart type.
        """
    )
    return [system_message, human_message]
