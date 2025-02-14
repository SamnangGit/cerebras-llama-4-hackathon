from pydantic import BaseModel, Field
from decimal import Decimal
from typing import Optional
class FuelTransactionBase(BaseModel):
    """Base Pydantic model for fuel transaction data"""
    transaction_date: str = Field(..., description="Date and time of the transaction")
    quantity: Decimal = Field(..., ge=0, description="Quantity of fuel dispensed")
    unit_price: Decimal = Field(..., ge=0, description="Price per unit of fuel")
    total_amount: Decimal = Field(..., ge=0, description="Total cost of the transaction")
    previous_km: Decimal = Field(..., ge=0, description="Previous kilometer reading")
    actual_km: Decimal = Field(..., ge=0, description="Current kilometer reading")
    consumption_rate: Optional[Decimal] = Field(None, ge=0, description="Fuel consumption rate")
    product_name: str = Field(..., description="Name of the fuel product")
    station_name: str = Field(..., description="Name of the fuel station")
    plate_number: str = Field(..., description="Plate number of the vehicle")
    station_address: str = Field(..., description="Address of the fuel station")

