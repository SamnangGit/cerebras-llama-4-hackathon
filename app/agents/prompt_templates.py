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
    message = HumanMessage(
                    content=[
                        {
                            "type": "text",
                            "text": prompt + "\n\n" + "Here is the schema of the database:" + str(schema)
                        }
                    ]
                )
    return message  


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
                You are a helpful assistant that generates HTML code for modern and beautiful using light color schema charts, 
                make sure it is responsive for mobile screen and provides detailed data analysis. 
                Focus on creating clear, interactive visualizations and insightful explanations of the data patterns.
                """
            )
    return [system_message, human_message]
