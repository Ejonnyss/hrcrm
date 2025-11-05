from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import os

# Database connection URL; default to Postgres used in docker-compose
DATABASE_URL = os.getenv("DATABASE_URL", "postgres://hrcrm:hrcrm@db:5432/hrcrm")

# Set up SQLAlchemy
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ORM models
class Vacancy(Base):
    __tablename__ = "vacancies"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    status = Column(String, nullable=False, default="open")


class Candidate(Base):
    __tablename__ = "candidates"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True, index=True)
    phone = Column(String, nullable=True)
    city = Column(String, nullable=True)


# Create tables if they don't exist
Base.metadata.create_all(bind=engine)


# Pydantic schemas
class VacancyCreate(BaseModel):
    title: str
    description: Optional[str] = None
    status: Optional[str] = "open"


class VacancyRead(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    status: str

    class Config:
        orm_mode = True


class CandidateCreate(BaseModel):
    full_name: str
    email: str
    phone: Optional[str] = None
    city: Optional[str] = None


class CandidateRead(BaseModel):
    id: int
    full_name: str
    email: str
    phone: Optional[str] = None
    city: Optional[str] = None

    class Config:
        orm_mode = True


app = FastAPI()


# Dependency to get DB session

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/health")
def health():
    return {"status": "ok"}


# Vacancy endpoints
@app.get("/vacancies", response_model=List[VacancyRead])
def list_vacancies(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Vacancy).offset(skip).limit(limit).all()


@app.post("/vacancies", response_model=VacancyRead)
def create_vacancy(vacancy: VacancyCreate, db: Session = Depends(get_db)):
    db_vacancy = Vacancy(**vacancy.dict())
    db.add(db_vacancy)
    db.commit()
    db.refresh(db_vacancy)
    return db_vacancy


# Candidate endpoints
@app.get("/candidates", response_model=List[CandidateRead])
def list_candidates(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Candidate).offset(skip).limit(limit).all()


@app.post("/candidates", response_model=CandidateRead)
def create_candidate(candidate: CandidateCreate, db: Session = Depends(get_db)):
    existing = db.query(Candidate).filter(Candidate.email == candidate.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Candidate with this email already exists")
    db_candidate = Candidate(**candidate.dict())
    db.add(db_candidate)
    db.commit()
    db.refresh(db_candidate)
    return db_candidate
