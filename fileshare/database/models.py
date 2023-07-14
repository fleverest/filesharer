import uuid

from sqlalchemy import UUID, Column, Computed, Index, Integer, DateTime, String, Boolean, ForeignKey, literal, select, text
from sqlalchemy.orm import column_property, relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_utils.types.ts_vector import TSVectorType

from fileshare.database.engine import Base
def to_tsvector_ix(*columns):
    s = " || ' ' || ".join(columns)
    return func.to_tsvector(literal('english'), text(s))


class Share(Base):

    """A model for sharing links to files"""

    __tablename__ = "share"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    created = Column(DateTime, server_default=func.now(), nullable=False)
    updated = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    file_id = Column(UUID(as_uuid=True), ForeignKey("file.id", ondelete="CASCADE"))
    file = relationship("File", back_populates="shares")

    key = Column(String, nullable=False, unique=True)
    expiry = Column(DateTime)
    download_limit = Column(Integer, server_default="0", nullable=False)
    download_count = Column(Integer, server_default="0", nullable=False)


class File(Base):

    """A model for files stored in the S3 bucket."""

    __tablename__ = "file"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    created = Column(DateTime, server_default=func.now(), nullable=False)
    updated = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    object_name = Column(String, nullable=False, unique=True)
    active = Column(Boolean, default=True)

    shares = relationship("Share", cascade="all, delete", passive_deletes=True, back_populates="file")
    share_count = column_property(select(func.count(Share.id)).where(Share.file_id==id).scalar_subquery())
    download_count = column_property(select(func.coalesce(func.sum(Share.download_count), 0)).where(Share.file_id==id).scalar_subquery())

    tsvector = Column(TSVectorType("tsvector", regconfig="english"), Computed("to_tsvector('english', regexp_replace(\"object_name\", '[^\w]+', ' ', 'g'))", persisted=True))

    __table_args__ = (
        Index(
            'idx_file_fts',
            tsvector,
            postgresql_using='gin'
        ),
    )


class Upload(Base):

    """A Model for upload keys"""

    __tablename__ = "upload"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    created = Column(DateTime, server_default=func.now(), nullable=False)
    updated = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    key = Column(String, nullable=False)
    expiry = Column(DateTime)
