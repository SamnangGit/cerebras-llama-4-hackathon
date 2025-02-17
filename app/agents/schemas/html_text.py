from pydantic import BaseModel, Field

class HTMLText(BaseModel):
    html: str = Field(description="The full HTML code for the chart")
    explanation: str = Field(description="A detailed explanation of the chart in detail")
    file_name: str = Field(description="The name of the file to save the HTML code")

