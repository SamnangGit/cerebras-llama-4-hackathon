from pydantic import BaseModel, Field

class SemanticTable(BaseModel):
    table_names: list[str] = Field(description="The name of the table")
    
    
