from sqlalchemy import Column, Integer, String, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from models.base_model import Base, BaseModel

class FuelTransaction(Base, BaseModel):
    __tablename__ = "fuel_transaction"

    transaction_id = Column(Integer, primary_key=True, autoincrement=True)
    station_id = Column(Integer, ForeignKey("station.station_id"))
    vehicle_id = Column(Integer, ForeignKey("vehicle.vehicle_id"))
    # driver_id = Column(Integer, ForeignKey("driver.driver_id"))
    product_id = Column(Integer, ForeignKey("product.product_id"))
    transaction_date = Column(String, nullable=False, index=True)
    quantity = Column(Numeric(10, 2), nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)
    previous_km = Column(Numeric(10, 1))
    actual_km = Column(Numeric(10, 1))
    consumption_rate = Column(Numeric(10, 2), nullable=True)

    station = relationship("Station", back_populates="transactions")
    vehicle = relationship("Vehicle", back_populates="transactions")
    # driver = relationship("Driver", back_populates="transactions")
    product = relationship("Product", back_populates="transactions")