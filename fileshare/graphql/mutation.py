import strawberry
from fileshare.graphql.file.mutations import FileMutation
from fileshare.graphql.share.mutations import ShareMutation

@strawberry.type
class Mutation(FileMutation, ShareMutation):
    @strawberry.field
    def ping(self) -> str:
        return "pong"
