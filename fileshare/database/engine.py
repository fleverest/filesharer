from fileshare.settings import settings

from sqlalchemy.ext.declarative import declarative_base

from typing import AsyncGenerator
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import configure_mappers

dbc = settings.database

creds = dbc.username
if dbc.username and dbc.password:
    creds += ":" + dbc.password + "@"

port = ""
if dbc.port:
    port = ":" + dbc.port

SQLALCHEMY_DATABASE_URL = f"{dbc.protocol}://{creds}{dbc.hostname}{port}/{dbc.database}"

connect_args = {}
if dbc.protocol == "sqlite":
    connect_args["check_same_thread"] = False

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, connect_args = connect_args)
configure_mappers()

async_session = async_sessionmaker(bind=engine, autoflush=False)

@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        async with session.begin():
            try:
                yield session
            finally:
                await session.close()

Base = declarative_base()
