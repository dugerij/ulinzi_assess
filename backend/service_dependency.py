"""
This file contains some utility functions for interacting with postgresql database.
"""

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine, exc
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import Session, sessionmaker

from backend.config import ASYNC_DATABASE_URL, DATABASE_URL
from backend.schemas import RequestLog
from backend.prediction_service import PredictionService

# Create a synchronous database session
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, autocommit=False, autoflush=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async_engine = create_async_engine(ASYNC_DATABASE_URL)
async_session = async_sessionmaker(async_engine, expire_on_commit=False)


async def init_db():
    """
    Initialize the database schema.
    """
    # Create all tables
    async with async_engine.begin() as conn:
        await conn.run_sync(RequestLog.metadata.create_all)


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Create and yield an async session.
    """
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except exc.SQLAlchemyError:
            await session.rollback()
            raise
        finally:
            await session.close()


AsyncDatabaseDependency = Annotated[AsyncSession, Depends(get_async_db)]
SyncDatabaseDependency = Annotated[Session, Depends(get_db)]


#################### Services Factory ####################
class ServiceFactory:
    """
    Factory class to manage and connect service instances
    """
    _instance = None
    _services = {}
    _initialized = False


    def __new__(cls):
        """
        Ensure that only one instance of ServiceFactory exists.
        """
        if cls._instance is None:
            cls._instance = super(ServiceFactory, cls).__new__(cls)
            return cls._instance
        
    @classmethod
    async def initialize_services(cls, db: AsyncDatabaseDependency):
        """
        Initialize all services.
        """
        if not cls._initialized:
            cls._services =await cls._create_async_services(db)
            cls._initialized = True

    @classmethod
    async def _create_async_services(cls, db: AsyncDatabaseDependency):
        """
        Create and return initialised services
        """
        pred_service = PredictionService(db)

        return {
            "prediction_service": pred_service
        }
    
    @classmethod
    async def get_service(cls, service_name: str, db: AsyncDatabaseDependency):
        """
        Get a service instance by name, initializing it if necessary.
        """
        await cls.initialize_services(db)
        return cls._services[service_name]


async def initialize_services():
    """
    Initialize the service factory and services.
    """
    async for db in get_async_db():
        await ServiceFactory.initialize_services(db)
        break

async def get_prediction_service(db: AsyncDatabaseDependency) -> PredictionService:
    """
    Get the prediction service instance.

    Args:
        db (AsyncDatabaseDependency): The database dependency.
    """
    return await ServiceFactory.get_service("prediction_service", db)

PredictionServiceDependency = Annotated[PredictionService, Depends(get_prediction_service)]
