import os

from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.environ.get('DB_HOST')
DB_PORT = os.environ.get('DB_PORT')
DB_NAME = os.environ.get('DB_NAME')
DB_USER = os.environ.get('DB_USER')
DB_PASS = os.environ.get('DB_PASS')
REDIS_HOST = os.environ.get('REDIS_HOST')

MODE = os.environ.get('MODE')


def db_url():
    return f'postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'


def get_mode():
    return MODE

# class Settings(BaseSettings):
#
#     MODE: str
#
#     DB_NAME: str
#     DB_HOST: str
#     DB_PORT: int
#     DB_USER: str
#     DB_PASS: str
#
#     @property
#     def db_url(self) -> str:
#         return f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
#
#     model_config = SettingsConfigDict(env_file=".env")
#
#
# settings = Settings()
