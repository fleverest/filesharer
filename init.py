#!/bin/env python
import asyncio
import uvicorn

from fileshare.main import app
from fileshare.database.engine import engine, Base

async def create_tables(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await engine.dispose()

if __name__=="__main__":
    print("Creating database")
    asyncio.run(create_tables(engine))
    print("Starting FastAPI app")
    uvicorn.run("init:app", host="0.0.0.0", port=5000, reload=True)
