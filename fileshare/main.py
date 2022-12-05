from fastapi import FastAPI # , Depends

#from fileshare.dependencies import example
from fileshare.database import engine
from fileshare.graphql.schema import graphql_app

engine.Base.metadata.create_all(bind=engine.engine)

app = FastAPI(dependencies=[])

app.include_router(graphql_app, prefix="/gql")

@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Hello World"}
