from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from models.base_model import Base, BaseModel

class Station(Base, BaseModel):
    __tablename__ = "station"

    station_id = Column(Integer, primary_key=True, autoincrement=True)
    station_name = Column(String(100), nullable=False)
    street_address = Column(String(255))

    transactions = relationship("FuelTransaction", back_populates="station")