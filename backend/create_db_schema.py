import asyncio
from app.database import engine, Base

async def create_tables():
    """
    Connects to the database and creates all tables based on the SQLAlchemy models.
    This is a utility script for development and should not be run in production
    without a proper migration strategy like Alembic.
    """
    async with engine.begin() as conn:
        print("Dropping all existing tables...")
        await conn.run_sync(Base.metadata.drop_all)
        print("Creating all tables...")
        await conn.run_sync(Base.metadata.create_all)
        print("Tables created successfully.")

if __name__ == "__main__":
    print("Running database schema creation script...")
    # Ensure you have a .env file with a valid DATABASE_URL
    asyncio.run(create_tables())
    print("Script finished.")
