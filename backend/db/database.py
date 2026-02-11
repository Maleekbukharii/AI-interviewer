from sqlalchemy import Column, String, Integer, Text, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import uuid

SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class InterviewSession(Base):
    __tablename__ = "sessions"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    company = Column(String)
    position = Column(String)
    difficulty = Column(String)
    history = Column(Text, default="") # Store as a simple string or JSON string

class InterviewLog(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("sessions.id"))
    question = Column(Text)
    answer = Column(Text)
    technical_score = Column(Integer)
    clarity_score = Column(Integer)
    structure_score = Column(Integer)
    confidence_score = Column(Integer)
    strengths = Column(Text)
    weaknesses = Column(Text)
    improvement_plan = Column(Text)

Base.metadata.create_all(bind=engine)
