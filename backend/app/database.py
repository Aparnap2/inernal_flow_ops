from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import settings
import app.models  # Import models to register them with SQLAlchemy

# Create an async engine to connect to the database
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,  # Set to True to see generated SQL statements
    future=True
)

# Create a factory for async sessions
AsyncSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# A base class for our models to inherit from
Base = declarative_base()

async def init_db():
    """Initialize the database by creating all tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    """
    Dependency that provides a database session for a single request.
    """
    async with AsyncSessionLocal() as session:
        yield session
