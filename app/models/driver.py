from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from models.base_model import Base, BaseModel

class Driver(Base, BaseModel):
    __tablename__ = "driver"
    driver_id = Column(Integer, primary_key=True, autoincrement=True)
    driver_name = Column(String(100))
    # transactions = relationship("FuelTransaction", back_populates="driver")
