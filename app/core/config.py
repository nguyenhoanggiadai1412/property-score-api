import os
from pathlib import Path

# Manual .env loading to avoid python-dotenv dependency
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
if env_path.exists():
    with open(env_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                os.environ[key.strip()] = val.strip()

class Settings:
    PROJECT_NAME: str = "Property Score API"
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql+psycopg2://postgres:123456@192.168.1.22:5433/gisdb"
    )

settings = Settings()
