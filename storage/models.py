from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

Base = declarative_base()

class RepositoryRecord(Base):
    __tablename__ = 'repositories'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    path = Column(String, nullable=False)
    last_analyzed = Column(DateTime, default=datetime.utcnow)
    
    results = relationship("AnalysisResultRecord", back_populates="repository")

class AnalysisResultRecord(Base):
    __tablename__ = 'analysis_results'
    
    id = Column(Integer, primary_key=True)
    repo_id = Column(Integer, ForeignKey('repositories.id'))
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Core Metrics
    health_score = Column(Float)
    coherence_score = Column(Float)
    risk_score = Column(Float)
    
    # Full Result Data (JSON)
    full_data = Column(JSON)
    
    repository = relationship("RepositoryRecord", back_populates="results")

def init_db(db_url="sqlite:///ai_collab.db"):
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    return engine

def get_session(engine):
    Session = sessionmaker(bind=engine)
    return Session()
