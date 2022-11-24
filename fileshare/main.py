from fastapi import FastAPI # , Depends

#from fileshare.dependencies import example
from fileshare.graphql.schema import graphql_app

app = FastAPI(dependencies=[])

app.include_router(graphql_app, prefix="/gql")

@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Hello World"}
