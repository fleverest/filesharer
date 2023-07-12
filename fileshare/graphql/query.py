import strawberry

from fileshare.graphql.file.queries import FileQuery
from fileshare.graphql.share.queries import ShareQuery

@strawberry.type
class Query(FileQuery, ShareQuery):
    @strawberry.field
    def ping(self) -> str:
        return "pong"
