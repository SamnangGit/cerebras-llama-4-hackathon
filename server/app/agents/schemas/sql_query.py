from pydantic import BaseModel, Field
from typing import Optional

class SQLQuery(BaseModel):
    query: str = Field(description="The SQL query to be executed")
    explanation: str = Optional  [str] 
    chart_type: str = Optional [str] 