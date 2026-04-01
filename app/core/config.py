import os

class Settings:
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5433/healthcare")
        self.test_database_url = os.getenv("TEST_DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5433/postgres")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "demo-key")
        self.debug = os.getenv("DEBUG", "true").lower() == "true"

settings = Settings()
