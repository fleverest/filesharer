import strawberry
from fileshare.graphql.file.mutations import FileMutation

@strawberry.type
class Mutation(FileMutation):
    @strawberry.field
    def ping(self) -> str:
        return "pong"
