import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
from models.base_model import Base
from models.fuel_transaction import FuelTransaction
from models.product import Product
from models.station import Station
from models.vehicle import Vehicle
from models.driver import Driver
from datetime import datetime
from models.analysis_history import AnalysisHistory

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
        engine, _ = self.get_db()
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
        try:
            engine, _ = self.get_db()
            with engine.connect() as connection:
                print(sql_query)
                result = connection.execute(text(sql_query))
                column_names = result.keys()
                data = result.fetchall()
                
                result_list = []
                for row in data:
                    result_list.append(dict(zip(column_names, row)))
            return result_list
        except Exception as e:
            raise Exception(f"Error executing SQL query: {str(e)}")
    
    def verify_tables(self):
        """
        Verify that tables were created in the database
        """
        engine, _ = self.get_db()
        existing_tables = Base.metadata.tables.keys()
        print("Created tables:", existing_tables)
        return existing_tables
    
    def get_or_create_record(self, db, model, unique_fields, **kwargs):
        """
        Helper method to get existing record or create new one
        unique_fields: dict of field names and values to check for existing records
        """
        try:
            # Check for existing record using unique fields
            instance = db.query(model).filter_by(**unique_fields).first()
            if instance:
                return instance
                
            # If no existing record, create new one with all fields
            instance = model(**kwargs)
            db.add(instance)
            db.flush()
            return instance
        except Exception as e:
            raise Exception(f"Error getting or creating record: {str(e)}")

    def save_fuel_transaction(self, fuel_transaction, driver_name):
        """Save fuel transaction with related records to the database"""
        engine, SessionLocal = self.get_db()
        last_record_ids = self.get_last_record_ids()
        last_product_id = last_record_ids["last_product_id"]
        last_station_id = last_record_ids["last_station_id"]
        last_vehicle_id = last_record_ids["last_vehicle_id"] 
        last_driver_id = last_record_ids["last_driver_id"]
        last_transaction_id = last_record_ids["last_fuel_transaction_id"]

        print(driver_name)
        
        with SessionLocal() as db:
            try:
                # Get or create related records using helper method
                product = self.get_or_create_record(
                    db,
                    Product,
                    unique_fields={"product_name": fuel_transaction.product_name},
                    product_id=last_product_id + 1,
                    product_name=fuel_transaction.product_name
                )
                
                station = self.get_or_create_record(
                    db,
                    Station,
                    unique_fields={"station_name": fuel_transaction.station_name},
                    station_id=last_station_id + 1,
                    station_name=fuel_transaction.station_name
                )
                
                vehicle = self.get_or_create_record(
                    db,
                    Vehicle,
                    unique_fields={"plate_number": fuel_transaction.plate_number},
                    vehicle_id=last_vehicle_id + 1,
                    plate_number=fuel_transaction.plate_number
                )
                
                driver = self.get_or_create_record(
                    db,
                    Driver,
                    unique_fields={"driver_name": driver_name},
                    driver_id=last_driver_id + 1,
                    driver_name=driver_name
                )

                # Create fuel transaction with the obtained IDs
                fuel_transaction_model = FuelTransaction(
                    transaction_id=last_transaction_id + 1,
                    product_id=product.product_id,
                    station_id=station.station_id,
                    vehicle_id=vehicle.vehicle_id,
                    driver_id=driver.driver_id,
                    transaction_date=self.convert_date_string(fuel_transaction.transaction_date),
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
                
    def save_analysis_history(self, analysis_history: AnalysisHistory):
        """Save analysis history to the database"""
        engine, SessionLocal = self.get_db()
        with SessionLocal() as db:
            try:
                last_analysis_id = self.get_last_record_ids()["last_analysis_id"]
                analysis_history_model = AnalysisHistory(
                    analysis_id=last_analysis_id + 1,
                    prompt=analysis_history.prompt,
                    file_path=analysis_history.file_path,
                    sql_statement=analysis_history.sql_statement,
                    explanation=analysis_history.explanation
                )
                db.add(analysis_history_model)
                db.commit()
                db.refresh(analysis_history_model)
                return analysis_history_model
            except Exception as e:
                db.rollback()
                raise Exception(f"Failed to save analysis history: {str(e)}")

    def convert_date_string(self, date_str: str) -> datetime:
        try:
            parsed_date = datetime.strptime(date_str, '%d/%m/%Y %H:%M')
            return parsed_date.replace(microsecond=419502)
        except ValueError as e:
            raise ValueError(f"Invalid date string format. Expected DD/MM/YYYY HH:mm, got: {date_str}") from e
        
    def get_last_record_ids(self) -> dict[str, int]:
        """Get the last record ids"""
        engine, SessionLocal = self.get_db()
        with SessionLocal() as db:
            last_analysis = db.query(AnalysisHistory).order_by(AnalysisHistory.analysis_id.desc()).first()
            last_fuel_transaction = db.query(FuelTransaction).order_by(FuelTransaction.transaction_id.desc()).first()
            last_product = db.query(Product).order_by(Product.product_id.desc()).first()
            last_station = db.query(Station).order_by(Station.station_id.desc()).first()
            last_vehicle = db.query(Vehicle).order_by(Vehicle.vehicle_id.desc()).first()
            last_driver = db.query(Driver).order_by(Driver.driver_id.desc()).first()
            return {
                "last_analysis_id": last_analysis.analysis_id if last_analysis else 0,
                "last_fuel_transaction_id": last_fuel_transaction.transaction_id if last_fuel_transaction else 0,
                "last_product_id": last_product.product_id if last_product else 0,
                "last_station_id": last_station.station_id if last_station else 0,
                "last_vehicle_id": last_vehicle.vehicle_id if last_vehicle else 0,
                "last_driver_id": last_driver.driver_id if last_driver else 0
            }
        

    def get_relationship_tables(self, table_name):
        engine, SessionLocal = self.get_db()  
        inspector = inspect(engine)
        
        # Verify the table exists
        if table_name not in inspector.get_table_names():
            return {
                "error": f"Table '{table_name}' does not exist",
                "status": False
            }
        
        try:
            # Get all columns for this table
            columns = [col['name'] for col in inspector.get_columns(table_name)]
            
            # Build query
            select_columns = ", ".join(columns)
            query = f"SELECT {select_columns} FROM {table_name}"
            
            # Create a session from the sessionmaker
            with SessionLocal() as session:
                # Execute with session
                result = session.execute(text(query))
                
                # Process the results
                table_data = {col: [] for col in columns}
                for row in result:
                    for i, col in enumerate(columns):
                        table_data[col].append(row[i])
                
                return {
                    "data": table_data,
                    "status": True
                }
        except Exception as e:
            return {
                "error": str(e),
                "status": False
            }
        

    def get_table_schemas_by_names(self, table_names):
        engine, _ = self.get_db()
        inspector = inspect(engine)
        schema_info = {}
        
        for table_name in table_names:
            # Verify the table exists
            if table_name not in inspector.get_table_names():
                schema_info[table_name] = {"error": f"Table '{table_name}' does not exist"}
                continue
                
            try:
                # Get column information with cleaned output
                columns = []
                for column in inspector.get_columns(table_name):
                    # Only include name and type in the column info
                    column_info = {
                        'name': column['name'],
                        'type': str(column['type'])
                    }
                    columns.append(column_info)
                
                # Get primary key information
                pk = inspector.get_pk_constraint(table_name)
                
                # Get foreign key information
                foreign_keys = inspector.get_foreign_keys(table_name)
                
                # Store all information for this table
                schema_info[table_name] = {
                    'columns': columns,
                    'primary_key': pk['constrained_columns'],
                    'foreign_keys': foreign_keys
                }
            except Exception as e:
                schema_info[table_name] = {"error": str(e)}
        
        return schema_info
    
    def get_last_n_records(self, table_names, n=3):
        engine, SessionLocal = self.get_db()
        results = {}
        
        with SessionLocal() as db:
            for table_name in table_names:
                # Direct query without table name validation
                query = text(f"SELECT * FROM {table_name} ORDER BY id DESC LIMIT {n}")
                result = db.execute(query)
                
                # Convert SQLAlchemy result objects to dictionaries
                rows = []
                for row in result.fetchall():
                    # Handle Row objects by converting to dict
                    if hasattr(row, '_mapping'):
                        # For SQLAlchemy 1.4+ Row objects
                        rows.append(dict(row._mapping))
                    elif hasattr(row, '_asdict'):
                        # For SQLAlchemy 1.3 RowProxy objects
                        rows.append(row._asdict())
                    else:
                        # Handle tuples (depends on your schema)
                        column_names = result.keys()
                        row_dict = {column_names[i]: value for i, value in enumerate(row)}
                        rows.append(row_dict)
                
                results[table_name] = rows
        
        return results