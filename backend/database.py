from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects.postgresql import JSONB # Best for Neon/Postgres
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    
    # Matches the back_populates in ResumeAnalysis
    analyses = relationship("ResumeAnalysis", back_populates="owner")

class ResumeAnalysis(Base):
    __tablename__= "resume_analysis"    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    job_description = Column(Text, nullable=True)     
    score = Column(Integer)
    
    # REMOVED 'status' here to match the stable/synchronous flow
    
    # Using JSONB is perfect for storing lists like ["Python", "Django"]
    skills = Column(JSONB, default=[])                             
    missing_skills = Column(JSONB, default=[])                     
    suggestions = Column(JSONB, default=[])
    
    owner = relationship("User", back_populates="analyses")

if __name__ == "__main__":
    try:
        Base.metadata.create_all(engine)
        print("✅ Tables created/verified successfully!")
    except Exception as e:
        print(f"❌ Connection failed: {e}")