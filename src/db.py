from sqlalchemy.ext.asyncio import create_async_engine

from src.config import db_url

DATABASE_URL = db_url()
engine = create_async_engine(DATABASE_URL)
