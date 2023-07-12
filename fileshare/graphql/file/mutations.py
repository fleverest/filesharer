from uuid import UUID
import strawberry
from strawberry.types import Info
from strawberry.file_uploads import Upload
from psycopg2.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError

from fileshare.database.engine import get_db
from fileshare.database.models import File
from fileshare.storage.minio import FileDeleteError, storage

from fileshare.graphql.file.types import AddFileError, AddFilesResult, FileType, RemoveFileError, RemoveFilesResult
from fileshare.storage.minio import FilePutError


@strawberry.type
class FileMutation:
    "A Mutation class for Files"

    @strawberry.mutation
    def add_files(
        self,
        info: Info,
        prefix: str,
        files: list[Upload]
        ) -> AddFilesResult:

        session = next(get_db())
        added: list[FileType] = []
        errors : list[AddFileError] = []

        for file in files:
            name = prefix + file.filename # noqa
            try:
                db_file = File(object_name=name, active=True)
                session.add(db_file)
                session.flush()
                session.refresh(db_file)
                added.append(FileType.from_instance(db_file))
                storage.put(name, file.file, file.size) # noqa
                session.commit()
            except FilePutError as e:
                errors.append(
                    AddFileError(
                        code="add_files_storage_error",
                        message=f"Could not add '{name}': storage backend failure."
                    )
                )
                session.rollback()
            except IntegrityError as e:
                if isinstance(e.orig, UniqueViolation):
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
                session.rollback()
        return AddFilesResult(added=added, errors=errors)

    @strawberry.mutation
    def remove_files(
        self,
        info: Info,
        prefix: str,
        filenames: list[str] | None = None,
        ids: list[UUID] | None = None,
        ) -> RemoveFilesResult:

        session = next(get_db())
        removed: list[FileType] = []
        errors: list[RemoveFileError] = []

        if filenames:
            if ids:
                for _ in ids + filenames:
                    errors.append(RemoveFileError(code="remove_files_malformed_request", message="Files can only be removed by ID or by filename, not both."))
                return RemoveFilesResult(removed=removed, errors=errors)
            files = session\
                .query(File)\
                .filter(
                    File.object_name.in_(
                        (*(prefix + name for name in filenames),)
                    )
                )\
                .all()
        elif ids:
            files = session\
                .query(File)\
                .filter(
                    File.id.in_(ids)
                )\
                .all()
        else:
            errors.append(RemoveFileError(code="remove_files_malformed_request", message="Files must be removed by ID or filename."))
            return RemoveFilesResult(removed=removed, errors=errors)

        for file in files:
            session.delete(file)
            try:
                storage.delete([str(file.object_name)])
            except FileDeleteError as e:
                errors = [
                    RemoveFileError(
                        code="remove_files_storage_backend_error",
                        message=f"Could not remove file '{filename}' from storage backend."
                    ) for filename in e.filenames
                ]
                session.rollback()
            removed.append(FileType.from_instance(file))
            session.commit()
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
