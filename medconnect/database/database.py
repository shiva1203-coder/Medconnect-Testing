import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base
from sqlalchemy.exc import SQLAlchemyError

# Base class for ORM models
Base = declarative_base()

# Global session (scoped for thread safety)
SessionLocal = None
engine = None


def init_db(app=None):
    """
    Initialize database engine and session.
    Must be called BEFORE using SessionLocal
    """
    global engine, SessionLocal

    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError("DATABASE_URL is not set in environment")

    try:
        engine = create_engine(
            database_url,
            pool_pre_ping=True,
            pool_recycle=300,
            echo=False
        )

        SessionLocal = scoped_session(
            sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=engine
            )
        )

        print("✅ Database connected successfully")

        if app:
            app.db_session = SessionLocal

    except SQLAlchemyError as e:
        raise RuntimeError(f"Database initialization failed: {e}")


def get_db():
    """
    Safe DB session generator
    """
    if SessionLocal is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_all():
    """
    Create tables safely
    """
    if engine is None:
        raise RuntimeError("Database engine not initialized. Call init_db() first.")

    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully")
