
from sqlalchemy import Column, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class TMDBRequest(Base):
    __tablename__ = 'tmdb_request'

    request_id = Column(Integer(), primary_key=True, autoincrement=True)
    request_type = Column(String(20), nullable=False)
    request_key = Column(Integer(),nullable=False)
    json_response = Column(JSONB)
    __table_args__ = (UniqueConstraint('request_key', 'request_type', name = 'request_key_type_UK'),)


