import strawberry

from fileshare.graphql.file.queries import FileQuery

@strawberry.type
class Query(FileQuery):
    @strawberry.field
    def hello(self) -> str:
        return "Hello World"
