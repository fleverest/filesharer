from fastapi import FastAPI

from fileshare.graphql.schema import graphql_app


app = FastAPI(dependencies=[])
app.include_router(graphql_app, prefix="/gql")
