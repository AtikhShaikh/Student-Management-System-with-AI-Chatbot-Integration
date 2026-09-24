from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# using sqlite for now, easy to set up locally
DATABASE_URL = "sqlite:///./students.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# this gets used in main.py as a dependency so every request gets its own db session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
