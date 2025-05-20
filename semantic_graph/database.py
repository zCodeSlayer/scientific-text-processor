from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from config import database_settings

DATABASE_URL = (
    "postgresql+psycopg://"
    f"{database_settings.DB_USER}:{database_settings.DB_PASSWORD}"
    f"@{database_settings.DB_HOST}:{database_settings.DB_PORT}/{database_settings.DB_NAME}"
)

db_engine = create_async_engine(DATABASE_URL, echo=True)
db_session = async_sessionmaker(db_engine, expire_on_commit=False)


async def get_session():
    async with db_session() as session:
        yield session
