from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

# SQLite requires "check_same_thread": False for concurrent FastAPI workers
engine = create_engine(
    settings.DATABASE_URL, 
    connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency injector yielding a database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()