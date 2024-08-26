import os

from dotenv import load_dotenv

load_dotenv()

DEFAULT_NUMBER_OF_MESSAGES = 1000

QUEUE_NAME = os.getenv("QUEUE_NAME", "sms")
RABBIT_HOST = os.getenv("RABBIT_HOST", "localhost")
MAX_CHARS_IN_SMS = 100

DB_NAME = os.getenv("POSTGRES_DB", "sms")
DB_USER = os.getenv("POSTGRES_USER", "sms")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "sms")
DB_HOST = os.getenv("POSTGRES_HOST", "postgres")
DB_PORT = os.getenv("POSTGRES_PORT", 5432)
