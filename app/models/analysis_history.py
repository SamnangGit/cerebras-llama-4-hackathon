from sqlalchemy import Column, Integer, String
from models.base_model import Base, BaseModel

class AnalysisHistory(Base, BaseModel):
    __tablename__ = "analysis_history"

    analysis_id = Column(Integer, primary_key=True, autoincrement=True)
    prompt = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    sql_statement = Column(String, nullable=False)
    explanation = Column(String, nullable=False)

