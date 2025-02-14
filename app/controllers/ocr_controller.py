from agents.model import GenerativeModel
from agents.schemas.fuel_transaction import FuelTransactionBase
from models.fuel_transaction import FuelTransaction
from models.product import Product
from models.station import Station
from models.vehicle import Vehicle
from models.init_db import get_db
from sqlalchemy.orm import Session

class OCRController:
    def __init__(self, model_name: str = "gemini-2.0-flash"):
        """Initialize OCR controller with specified model."""
        self.model = GenerativeModel(model_name=model_name)
        _, self.SessionLocal = get_db()

    def ocr_structured_output(self, image_path: str) -> FuelTransactionBase:
        try:
            prompt = (
                "Extract all visible text from this image. "
                "Return only the extracted text, maintaining its original formatting."
            )
            
            result = self.model.generate_text(prompt, image_path)
            self.save_to_database(result)
            return result
            
        except Exception as e:
            raise Exception(f"OCR processing failed: {str(e)}")
        


    def get_or_create_record(self, db: Session, model, **kwargs):
        """Helper method to get existing record or create new one"""
        instance = db.query(model).filter_by(**kwargs).first()
        if instance:
            return instance
        
        instance = model(**kwargs)
        db.add(instance)
        db.flush()
        return instance

    def save_to_database(self, fuel_transaction: FuelTransactionBase):
        with self.SessionLocal() as db:
            try:
                # Get or create related records using helper method
                product = self.get_or_create_record(
                    db,
                    Product,
                    product_name=fuel_transaction.product_name
                )
                
                station = self.get_or_create_record(
                    db,
                    Station,
                    station_name=fuel_transaction.station_name
                )
                
                vehicle = self.get_or_create_record(
                    db,
                    Vehicle,
                    plate_number=fuel_transaction.plate_number
                )
                
                # Create fuel transaction with the obtained IDs
                fuel_transaction_model = FuelTransaction(
                    product_id=product.product_id,
                    station_id=station.station_id,
                    vehicle_id=vehicle.vehicle_id,
                    transaction_date=fuel_transaction.transaction_date,
                    quantity=fuel_transaction.quantity,
                    unit_price=fuel_transaction.unit_price,
                    total_amount=fuel_transaction.total_amount,
                    previous_km=fuel_transaction.previous_km,
                    actual_km=fuel_transaction.actual_km,
                    consumption_rate=fuel_transaction.consumption_rate,
                )
                
                db.add(fuel_transaction_model)
                db.commit()
                db.refresh(fuel_transaction_model)
                
                return fuel_transaction_model
                
            except Exception as e:
                db.rollback()
                raise Exception(f"Failed to save transaction: {str(e)}")

