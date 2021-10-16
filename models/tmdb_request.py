
from sqlalchemy import Column, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from helpers import get_db_connection

Base = declarative_base()

class TMDBRequest(Base):
    __tablename__ = 'tmdb_requests'

    request_id = Column(Integer(), primary_key=True, autoincrement=True)
    request_type = Column(String(20), nullable=False)
    request_key = Column(Integer(),nullable=False)
    request_text = Column(String(100), nullable=False)
    response_status_code = Column(Integer(), nullable=False)
    response_json = Column(JSONB)
    __table_args__ = (UniqueConstraint('request_key', 'request_type', name = 'request_key_type_UK'),)


DB_URL =  get_db_connection()
engine = create_engine(DB_URL)
Base.metadata.create_all(engine)




