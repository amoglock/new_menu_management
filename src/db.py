from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import db_url

DATABASE_URL = db_url()
engine = create_engine(DATABASE_URL)
Session = sessionmaker(engine)
