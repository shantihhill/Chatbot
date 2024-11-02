from app.constants import *
from sqlalchemy import create_engine, Column, Integer, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

#setting up flag database and session
engine = create_engine(FLAGS_DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

#class for flag data for database
class FlagData(Base):
    __tablename__ = "flag_data"

    id = Column(Integer, primary_key=True, index=True)
    chat = Column(Text)
    comment = Column(Text)
    date = Column(DateTime, default=datetime.now())

Base.metadata.create_all(bind=engine)

#getting current session of database
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()