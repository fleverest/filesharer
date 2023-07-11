import strawberry

from fileshare.graphql.file.queries import FileQuery

@strawberry.type
class Query(FileQuery):
    @strawberry.field
    def ping(self) -> str:
        return "pong"
