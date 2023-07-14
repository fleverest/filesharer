from uuid import UUID
from sqlalchemy import select
import strawberry
from strawberry.types import Info
from strawberry.file_uploads import Upload
from asyncpg.exceptions import UniqueViolationError
from sqlalchemy.exc import IntegrityError

from fileshare.database.engine import get_session
from fileshare.database.models import File
from fileshare.storage.minio import FileDeleteError, storage

from fileshare.graphql.file.types import AddFileError, AddFilesResult, FileType, RemoveFileError, RemoveFilesResult
from fileshare.storage.minio import FilePutError


@strawberry.type
class FileMutation:
    "A Mutation class for Files"

    @strawberry.mutation
    async def add_files(
        self,
        info: Info,
        prefix: str,
        files: list[Upload]
        ) -> AddFilesResult:

        added: list[FileType] = []
        errors : list[AddFileError] = []

        for file in files:
            async with get_session() as session:
                name = prefix + file.filename # noqa
                try:
                    db_file = File(object_name=name, active=True)
                    session.add(db_file)
                    await session.flush()
                    await session.refresh(db_file)
                    storage.put(name, file.file, file.size) # noqa
                    added.append(FileType.from_instance(db_file))
                    await session.commit()
                except FilePutError as e:
                    errors.append(
                        AddFileError(
                            code="add_files_storage_error",
                            message=f"Could not add '{name}': storage backend failure."
                        )
                    )
                    print(e)
                    await session.rollback()
                except IntegrityError as e:
                    if isinstance(e.orig.__cause__, UniqueViolationError):
                        errors.append(
                            AddFileError(
                                code="add_files_database_unique_violation_error",
                                message=f"Could not add '{name}': file already exists in database."
                            )
                        )
                    else:
                        errors.append(
                            AddFileError(
                                code="add_files_unknown_error",
                                message=f"Could not add '{name}': unknown database integrity error."
                            )
                        )
                        print(e)
                    await session.rollback()
        return AddFilesResult(added=added, errors=errors)

    @strawberry.mutation
    async def remove_files(
        self,
        info: Info,
        prefix: str,
        filenames: list[str] | None = None,
        ids: list[UUID] | None = None,
        ) -> RemoveFilesResult:

        async with get_session() as session:
            removed: list[FileType] = []
            errors: list[RemoveFileError] = []

            if filenames:
                if ids:
                    for _ in ids + filenames:
                        errors.append(RemoveFileError(code="remove_files_malformed_request", message="Files can only be removed by ID or by filename, not both."))
                    return RemoveFilesResult(removed=removed, errors=errors)
                files_query = select(File).filter(File.object_name.in_((*(prefix + name for name in filenames),)))
            elif ids:
                files_query = select(File).filter(File.id.in_(ids))
            else:
                errors.append(RemoveFileError(code="remove_files_malformed_request", message="Files must be removed by ID or filename."))
                return RemoveFilesResult(removed=removed, errors=errors)
            result = await session.execute(files_query)
            files = result.scalars().all()

            for file in files:
                await session.delete(file)
                try:
                    storage.delete([str(file.object_name)])
                except FileDeleteError as e:
                    errors = [
                        RemoveFileError(
                            code="remove_files_storage_backend_error",
                            message=f"Could not remove file '{filename}' from storage backend."
                        ) for filename in e.filenames
                    ]
                    await session.rollback()
                removed.append(FileType.from_instance(file))
                await session.commit()
            if filenames:
                for filename in filenames:
                    if prefix+filename not in list(map(lambda f: str(f.object_name), files)):
                        errors.append(
                            RemoveFileError(
                                code="remove_files_file_not_found",
                                message=f"Could not remove file '{filename}': file not found.'"
                            )
                        )
            elif ids:
                for i in ids:
                    if i not in list(map(lambda f: f.id, files)):
                        errors.append(
                            RemoveFileError(
                                code="remove_files_file_not_found",
                                message=f"Could not remove file by id '{i}': file not found.'"
                            )
                        )

            return RemoveFilesResult(removed=removed, errors=errors)
