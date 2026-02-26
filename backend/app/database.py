import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://augur:postgres@localhost:5432/augur")
TIMESCALE_URL = os.getenv("TIMESCALE_URL", "postgresql://augur:timescale@localhost:5433/augur_ts")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

timescale_engine = create_engine(TIMESCALE_URL)
TimescaleSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=timescale_engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_ts_db():
    db = TimescaleSessionLocal()
    try:
        yield db
    finally:
        db.close()
