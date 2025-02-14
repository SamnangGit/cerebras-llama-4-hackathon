from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from models.base_model import Base, BaseModel

class Vehicle(Base, BaseModel):
    __tablename__ = "vehicle"

    vehicle_id = Column(Integer, primary_key=True, autoincrement=True)
    plate_number = Column(String(20), index=True)

    transactions = relationship("FuelTransaction", back_populates="vehicle")
