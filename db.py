import os

import pymysql
from dotenv import load_dotenv

# Read the settings (password etc.) from the .env file
load_dotenv()


def get_connection():
    """Open a new MySQL connection. Rows come back as dictionaries."""
    return pymysql.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "research_portal"),
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
        charset="utf8mb4",
    )
