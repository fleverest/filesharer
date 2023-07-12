import strawberry
from strawberry.types import Info
from psycopg2.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError
from uuid import UUID
from datetime import datetime

from fileshare.database.engine import get_db
from fileshare.database.models import File, Share

from fileshare.graphql.file.types import FileNotFoundError, FileType
from fileshare.graphql.share.types import ShareType, AddShareError, RemoveShareError, RemoveSharesResult


@strawberry.type
class ShareMutation:
    """A class containing the Shares mutations"""

    @strawberry.mutation
    def add_share(
        self,
        info: Info,
        file_id: UUID,
        key: str,
        expiry: datetime | None = None,
        download_limit: int | None = None
    ) -> ShareType | AddShareError | FileNotFoundError:

        session = next(get_db())
        file = session.query(File).filter(File.id == file_id).first()
        if not file:
            return FileNotFoundError(code="file_not_found", message=f"File with {id=} was not found in the database.")
        try:
            db_share = Share(file_id=file_id, key=key, expiry=expiry, download_limit=download_limit)
            session.add(db_share)
            session.flush()
            session.refresh(db_share)
            session.commit()
        except IntegrityError as e:
            session.rollback()
            if isinstance(e.orig, UniqueViolation):
                return AddShareError(code="add_share_database_unique_violation_error", message=f"Could not add share: key already in use.")
            else:
                return AddShareError(code="add_share_unknown_error", message="Could not add share: unknown database integrity error.")
        return ShareType.from_instance(db_share)

    @strawberry.mutation
    def remove_shares(
        self,
        info: Info,
        ids: list[UUID] | None,
        keys: list[str] | None,
    ) -> RemoveSharesResult:

        session = next(get_db())
        removed = []
        errors = []

        if ids is not None:
            if keys is not None:
                for _ in ids + keys:
                    errors.append(RemoveShareError(code="remove_shares_malformed_request", message="Shares can only be removed by ID or by key, not both."))
            shares = session.query(Share).filter(Share.id.in_(ids)).all()
        elif keys is not None:
            shares = session.query(Share).filter(Share.key.in_(keys)).all()
        else:
            errors.append(RemoveShareError(code="remove_shares_malformed_request", message="Shares must be removed by ID or key."))
            return RemoveSharesResult(removed=removed, errors=errors)

        for share in shares:
            session.delete(share)
            removed.append(ShareType.from_instance(share))
            session.commit()

        return RemoveSharesResult(removed=removed, errors=errors)
