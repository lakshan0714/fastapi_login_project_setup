
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
# Load environment variables from .env file
load_dotenv(override=True)

# Get individual components from environment variables
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")  # Default to 5432 if not provided
DB_NAME = os.getenv("DB_NAME")


# Construct database URLs dynamically
DATABASE_URL_ASYNC = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
DATABASE_URL_SYNC = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


# Create an asynchronous engine and session factory
engine = create_async_engine(DATABASE_URL_ASYNC, echo=True, future=True)
AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


# Create a synchronous engine and session factory
sync_engine = create_engine(DATABASE_URL_SYNC, echo=True)
SessionLocal = sessionmaker(bind=sync_engine, class_=Session, expire_on_commit=False)


# Declare the base class for ORM models
Base = declarative_base()


async def get_db():
    """
    Provides an async database session.
    Yields:
        AsyncSession: An asynchronous SQLAlchemy database session.
    """
    async with AsyncSessionLocal() as db:
        yield db

