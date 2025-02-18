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
                            1. Use PostgreSQL date/time functions like EXTRACT, DATE_PART instead of SQLite functions
                            2. Use proper PostgreSQL type casting with '::'
                            3. Follow PostgreSQL best practices for aggregations and grouping
                            4. Use appropriate PostgreSQL-specific features when needed (e.g., INTERVAL for date arithmetic)
                            5. Ensure all generated queries are compatible with PostgreSQL syntax
                            6. Use appropriate PostgreSQL window functions when needed
                            7. Format queries for readability with proper indentation
                            """
                )
    return [system_message, human_message]  


def generate_html_text_promp(prompt: str, data: str):
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
        You are a helpful assistant that generates HTML code for modern, responsive and visually appealing charts using different light color schemes. 
        When explaining the chart, act as a data analyst by:
        1. Highlighting key trends, outliers, or significant comparisons in the data
        2. Explaining what the visualization reveals 
        3. Suggesting actionable recommendations based on the patterns
        4. Pointing out potential business implications
        5. Make sure the explanation is not too long and not too short
        6. Make sure the explanation is in bullet points
        Avoid discussing technical implementation details like responsiveness or design elements.
        """
    )
    return [system_message, human_message]
