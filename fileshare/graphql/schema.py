import strawberry

from fileshare.graphql.query import Query
from strawberry.fastapi import GraphQLRouter


schema = strawberry.Schema(Query)
graphql_app = GraphQLRouter(schema)
