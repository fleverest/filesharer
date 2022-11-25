from minio import Minio
from datetime import timedelta

from fileshare.settings import settings
from fileshare.settings.minio import MinioSettings


class BucketDoesNotExist(Exception):
    """Exception raised when the minio bucket is missing.

    Attributes:
      message -- An explanation of the error.
      bucket -- The missing bucket.
    """
    def __init__(self, message: str, bucket: str) -> None:
        self.message = message
        self.bucket = bucket
        super().__init__(self.message)


class MinioStorage:

    """A storage interface using Minio"""

    def __init__(self, conf: MinioSettings | None = None) -> None:
        if not conf:
            conf = settings.minio

        self._endpoint = conf.endpoint
        self._access_key = conf.access_key
        self._secret_key = conf.secret_key
        self._bucket = conf.bucket
        self._upload_expire = timedelta(seconds=conf.upload_expire)
        self._download_expire = timedelta(seconds=conf.download_expire)

        self._session = None

    @property
    def session(self) -> Minio:
        """Retrieves the (or starts a) minio client session"""
        if not self._session:
            self._session = Minio(
                endpoint=self._endpoint,
                access_key=self._access_key,
                secret_key=self._secret_key
            )

        if not self._session.bucket_exists(self._bucket):
            raise BucketDoesNotExist(
                    "The specified bucket was not found on the Minio server.",
                    self._bucket)

        return self._session

    def delete(self, name: str) -> None:
        """Deletes a stored object"""
        self.session.remove_object(self._bucket, name)

    def presigned_get(self, name: str, expires: timedelta | None = None) -> str:
        """Creates a signed download url for the object"""
        if not expires:
            expires = self._download_expire
        return self.session.presigned_get_object(self._bucket, name, expires)

    def presigned_put(self, name: str, expires: timedelta | None = None) -> str:
        """Creates a signed upload url for the object"""
        if not expires:
            expires = self._upload_expire
        return self.session.presigned_put_object(self._bucket, name, expires)


storage = MinioStorage()
