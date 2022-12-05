from fileshare.settings import settings

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

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

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args = connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

Base = declarative_base()
