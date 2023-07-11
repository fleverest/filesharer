import strawberry

from fileshare.graphql.query import Query
from fileshare.graphql.mutation import Mutation
from strawberry.fastapi import GraphQLRouter


schema = strawberry.Schema(query=Query, mutation=Mutation)
graphql_app = GraphQLRouter(schema)
