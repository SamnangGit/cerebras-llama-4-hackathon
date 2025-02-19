from pydantic import BaseModel, Field

class SQLQuery(BaseModel):
    query: str = Field(description="The SQL query to be executed")
    explanation: str = Field(description="The explanation of the SQL query")
    chart_type: str = Field(description="The type of chart to be used")