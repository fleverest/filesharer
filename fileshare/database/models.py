# TODO: Use uuid for postgres

from sqlalchemy import Column, Integer, DateTime, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from fileshare.database.engine import Base

class File(Base):

    """A model for files stored in the S3 bucket."""

    __tablename__ = "file"

    id = Column(Integer, primary_key=True, index=True)
    created = Column(DateTime, server_default=func.now())
    updated = Column(DateTime, onupdate=func.now())

    file_name = Column(String, null=False, unique=True)
    object_name = Column(String, null=False, unique=True)
    active = Column(Boolean, default=True)

    shares = relationship("Share", back_populates="file")


class Share(Base):

    """A model for sharing links to files"""

    __tablename__ = "share"

    id = Column(Integer, primary_key=True, index=True)
    created = Column(DateTime, server_default=func.utcnow())
    updated = Column(DateTime, onupdate=func.utcnow())

    file_id = Column(Integer, ForeignKey("file.id"))
    file = relationship("File", back_populates="shares")

    key = Column(String, null=False)
    expiry = Column(DateTime)
    download_limit = Column(Integer, null=False)
    download_count = Column(Integer, null=False)

class Upload(Base):

    """A Model for upload keys"""

    __tablename__ = "upload"

    id = Column(Integer, primary_key=True, index=True)
    created = Column(DateTime, server_default=func.utcnow())
    updated = Column(DateTime, onupdate=func.utcnow())

    key = Column(String, null=False)
    expiry = Column(DateTime)
