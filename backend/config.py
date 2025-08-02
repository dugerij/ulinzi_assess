import os

from dotenv import load_dotenv

load_dotenv()

ASYNC_DATABASE_URL = os.getenv("ASYNC_DATABASE_URL", "")
DATABASE_URL = os.getenv("DATABASE_URL", "")

ENV = os.getenv("ENV", "development")
API_VERSION = os.getenv("API_VERSION", "/api/v1")
SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")