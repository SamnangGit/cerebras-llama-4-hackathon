from sqlalchemy import create_engine
from models.base_model import Base
import os
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
from models.base_model import Base
from models.driver import Driver
from models.product import Product
from models.station import Station
from models.vehicle import Vehicle
from models.fuel_transaction import FuelTransaction

load_dotenv(override=True)
DB_CONNECTION = os.getenv("DB_CONNECTION")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DATABASE = os.getenv("DB_DATABASE")

DATABASE_URL = f"{DB_CONNECTION}://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}"

def get_db():
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return engine, SessionLocal

def init_db():
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return engine, SessionLocal



# You can add a function to verify tables were created
def verify_tables():
    engine, _ = init_db()
    existing_tables = Base.metadata.tables.keys()
    print("Created tables:", existing_tables)
    return existing_tables