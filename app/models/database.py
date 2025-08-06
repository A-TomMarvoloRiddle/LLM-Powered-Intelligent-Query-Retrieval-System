from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from app.config.settings import settings

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class DocumentQuery(Base):
    __tablename__ = "document_queries"
    
    id = Column(Integer, primary_key=True, index=True)
    document_url = Column(String, nullable=False)
    document_name = Column(String, nullable=True)
    questions = Column(JSON, nullable=False)
    retrieved_chunks = Column(JSON, nullable=False)
    answers = Column(JSON, nullable=False)
    processing_time = Column(Integer, nullable=True)  # in milliseconds
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# Create tables
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()