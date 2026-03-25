import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base
from sqlalchemy.exc import SQLAlchemyError

Base = declarative_base()
SessionLocal = None
engine = None


def _engine_kwargs(database_url: str):
    kwargs = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
        "echo": False,
    }
    if database_url.startswith("sqlite"):
        kwargs["connect_args"] = {"check_same_thread": False}
    return kwargs


def init_db(app=None):
    global engine, SessionLocal

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is not set in environment")

    try:
        engine = create_engine(database_url, **_engine_kwargs(database_url))
        SessionLocal = scoped_session(
            sessionmaker(autocommit=False, autoflush=False, bind=engine)
        )

        if app:
            app.db_session = SessionLocal
    except SQLAlchemyError as exc:
        raise RuntimeError(f"Database initialization failed: {exc}")


def get_db():
    if SessionLocal is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_all():
    if engine is None:
        raise RuntimeError("Database engine not initialized. Call init_db() first.")

    Base.metadata.create_all(bind=engine)
