import strawberry
from uuid import UUID
from strawberry.types import Info

from fileshare.database.crud import get_file, get_files
from fileshare.database.engine import get_db
from fileshare.database.models import File
from fileshare.graphql.file.inputs import FileFilterInput, FileSortInput
from fileshare.graphql.file.types import FileType
from fileshare.graphql.types import CountableConnection, PageInfo

@strawberry.type
class FileQuery:
    """A query class for Files"""

    @strawberry.field
    def file(
        self,
        info: Info,
        id: UUID
    ) -> FileType | None:

        file_dict = await get_file()
        # TODO: check info for authentication
        session = next(get_db())
        try:
            file = session.query(File).filter(File.id == id).first()
            return FileType(**file.__dict__)
        except:
            return


    @strawberry.field
    def files(
        self,
        info: Info,
        filter: FileFilterInput,
        sort: FileSortInput,
        before: str | None,
        after: str | None,
        first: int | None,
        last: int | None
    ) -> CountableConnection[FileType]:
        return CountableConnection(
            count=0,
            page_info=PageInfo(has_next_page=False, has_previous_page=False, start_cursor="", end_cursor=""),
            edges=[]
        )
