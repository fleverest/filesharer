from sqlalchemy import select
import strawberry
from strawberry.types import Info
from asyncpg.exceptions import UniqueViolationError
from sqlalchemy.exc import IntegrityError
from uuid import UUID
from datetime import datetime

from fileshare.database.engine import get_session
from fileshare.database.models import File, Share

from fileshare.graphql.file.types import FileNotFoundError, FileType
from fileshare.graphql.share.types import EditShareError, ShareType, AddShareError, RemoveShareError, RemoveSharesResult


@strawberry.type
class ShareMutation:
    """A class containing the Shares mutations"""

    @strawberry.mutation
    async def add_share(
        self,
        info: Info,
        file_id: UUID,
        key: str,
        expiry: datetime | None = None,
        download_limit: int | None = None
    ) -> ShareType | AddShareError | FileNotFoundError:

        async with get_session() as session:
            file_query = select(File).filter(File.id == file_id)
            result = await session.execute(file_query)
            file = result.scalar()
            if not file:
                return FileNotFoundError(code="file_not_found", message=f"File with {id=} was not found in the database.")
            try:
                db_share = Share(file_id=file_id, key=key, expiry=expiry, download_limit=download_limit)
                session.add(db_share)
                await session.flush()
                await session.refresh(db_share)
                share = ShareType.from_instance(db_share)
                await session.commit()
            except IntegrityError as e:
                await session.rollback()
                if isinstance(e.orig.__cause__, UniqueViolationError):
                    return AddShareError(code="add_share_database_unique_violation_error", message=f"Could not add share: key already in use.")
                else:
                    return AddShareError(code="add_share_unknown_error", message="Could not add share: unknown database integrity error.")
            return share

    @strawberry.mutation
    async def remove_shares(
        self,
        info: Info,
        ids: list[UUID] | None,
        keys: list[str] | None,
    ) -> RemoveSharesResult:

        removed = []
        errors = []

        async with get_session() as session:

            if ids is not None:
                if keys is not None:
                    for _ in ids + keys:
                        errors.append(RemoveShareError(code="remove_shares_malformed_request", message="Shares can only be removed by ID or by key, not both."))
                shares_query = select(Share).filter(Share.id.in_(ids))
            elif keys is not None:
                shares_query = select(Share).filter(Share.key.in_(keys))
            else:
                errors.append(RemoveShareError(code="remove_shares_malformed_request", message="Shares must be removed by ID or key."))
                return RemoveSharesResult(removed=removed, errors=errors)

            result = await session.execute(shares_query)
            shares = result.scalars().all()

            for share in shares:
                await session.delete(share)
                removed.append(ShareType.from_instance(share))

            await session.commit()
        return RemoveSharesResult(removed=removed, errors=errors)

    @strawberry.mutation
    async def edit_share(
        self,
        info: Info,
        id: UUID | None = None,
        key: str | None = None,
        new_expiry: datetime | None = None,
        new_download_limit: int | None = None,
        new_key: str | None = None
    ) -> ShareType | EditShareError:

        async with get_session() as session:
            if id is not None:
                if key is not None:
                    return EditShareError(code="edit_share_malformed_request", message="Shares can only be selected for editing via key or id, not both.")
                share_query = select(Share).filter(Share.id==id)
            elif key is not None:
                share_query = select(Share).filter(Share.key==key)
            else:
                return EditShareError(code="edit_share_malformed_request", message="Shares can only be selected for editing via key or id.")

            result = await session.execute(share_query)
            share = result.scalar()
            if share is None:
                if id is not None:
                    return EditShareError(code="share_not_found", message=f"No share found with {id=}.")
                if key is not None:
                    return EditShareError(code="share_not_found", message=f"No share found with {key=}.")
            if new_expiry is not None:
                share.expiry = new_expiry
            if new_download_limit is not None:
                share.download_limit = new_download_limit
            if new_key is not None:
                share.key = new_key
            out = ShareType.from_instance(share)
            try:
                await session.commit()
            except IntegrityError as e:
                if isinstance(e.orig.__cause__, UniqueViolationError):
                    return EditShareError(code="edit_share_invalid_new_key", message=f"A share already exists with key '{new_key}'.")
                else:
                    return EditShareError(code="edit_share_unknown_error", message=f"An unknown error has occurred.")
            return out
