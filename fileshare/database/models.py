import uuid

from sqlalchemy import Column, Integer, DateTime, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID

from fileshare.database.engine import Base

class File(Base):

    """A model for files stored in the S3 bucket."""

    __tablename__ = "file"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    created = Column(DateTime, server_default=func.now())
    updated = Column(DateTime, onupdate=func.now())

    file_name = Column(String, nullable=False, unique=True)
    object_name = Column(String, nullable=False, unique=True)
    active = Column(Boolean, default=True)

    shares = relationship("Share", cascade="all, delete", passive_deletes=True, back_populates="file")

    def as_dict(self):
        return {
            "id": self.id,
            "created": self.created,
            "updated": self.updated,
            "file_name": self.file_name,
            "active": self.active,
        }

file_search_fields = [File.file_name, File.object_name]

class Share(Base):

    """A model for sharing links to files"""

    __tablename__ = "share"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    created = Column(DateTime, server_default=func.now())
    updated = Column(DateTime, onupdate=func.now())

    file_id = Column(UUID(as_uuid=True), ForeignKey("file.id"))
    file = relationship("File", back_populates="shares")

    key = Column(String, nullable=False)
    expiry = Column(DateTime)
    download_limit = Column(Integer, nullable=False)
    download_count = Column(Integer, nullable=False)

class Upload(Base):

    """A Model for upload keys"""

    __tablename__ = "upload"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    created = Column(DateTime, server_default=func.now())
    updated = Column(DateTime, onupdate=func.now())

    key = Column(String, nullable=False)
    expiry = Column(DateTime)
