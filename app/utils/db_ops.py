import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
from models.base_model import Base
from models.fuel_transaction import FuelTransaction
from models.product import Product
from models.station import Station
from models.vehicle import Vehicle



class DBOps:
    def __init__(self):
        load_dotenv(override=True)
        
        self.DB_CONNECTION = os.getenv("DB_CONNECTION")
        self.DB_HOST = os.getenv("DB_HOST")
        self.DB_PORT = os.getenv("DB_PORT")
        self.DB_USERNAME = os.getenv("DB_USERNAME")
        self.DB_PASSWORD = os.getenv("DB_PASSWORD")
        self.DB_DATABASE = os.getenv("DB_DATABASE")
        
        self.DATABASE_URL = f"{self.DB_CONNECTION}://{self.DB_USERNAME}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_DATABASE}"
    
    def get_db(self):
        """
        Get database engine and session factory
        """
        engine = create_engine(self.DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        return engine, SessionLocal
    
    def init_db(self):
        """
        Initialize the database by creating tables defined in the models
        """
        engine = create_engine(self.DATABASE_URL)
        Base.metadata.create_all(bind=engine)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        return engine, SessionLocal
    
    def get_schema_info(self):
        """
        Get detailed schema information including tables, columns, and their properties
        """
        engine, _ = self.init_db()
        inspector = inspect(engine)
        schema_info = {}
        
        # Get all table names
        for table_name in inspector.get_table_names():
            columns = []
            for column in inspector.get_columns(table_name):
                column_info = {
                    'name': column['name'],
                    'type': str(column['type']),
                    'nullable': column['nullable'],
                    'default': str(column['default']) if column['default'] else None,
                }
                columns.append(column_info)
            
            pk = inspector.get_pk_constraint(table_name)
            
            foreign_keys = inspector.get_foreign_keys(table_name)
            
            # Store all information for this table
            schema_info[table_name] = {
                'columns': columns,
                'primary_key': pk['constrained_columns'],
                'foreign_keys': foreign_keys
            }
        
        return schema_info
    
    def execute_sql_query(self, sql_query: str):
        """
        Execute a raw SQL query and return the result as a list of dictionaries
        """
        engine, _ = self.init_db()
        with engine.connect() as connection:
            result = connection.execute(text(sql_query))
            column_names = result.keys()
            data = result.fetchall()
            
            result_list = []
            for row in data:
                result_list.append(dict(zip(column_names, row)))
        
        return result_list
    
    def verify_tables(self):
        """
        Verify that tables were created in the database
        """
        engine, _ = self.init_db()
        existing_tables = Base.metadata.tables.keys()
        print("Created tables:", existing_tables)
        return existing_tables
    
    def get_or_create_record(self, db, model, **kwargs):
        """Helper method to get existing record or create new one"""
        instance = db.query(model).filter_by(**kwargs).first()
        if instance:
            return instance
        instance = model(**kwargs)
        db.add(instance)
        db.flush()
        return instance

    def save_fuel_transaction(self, fuel_transaction):
        """Save fuel transaction with related records to the database"""
        engine, SessionLocal = self.get_db()
        
        with SessionLocal() as db:
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