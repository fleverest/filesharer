from minio import Minio
from minio.deleteobjects import DeleteObject
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

class FilePutError(Exception):
    """Exception raised when the client fails to put a new file into the bucket.

    Attributes:
        message -- An explanation of the error.
        file_name -- The name of the file which could not be uploaded.
        bucket -- The name of the bucket which the file could not be uploaded to.
        minio_args -- The original minio error raised.
    """
    def __init__(self, message: str, bucket: str, file_name: str, args) -> None:
        self.message = message
        self.bucket = bucket
        self.file_name = file_name
        self.minio_args = args

class FileDeleteError(Exception):
    """Exception raised when the client fails to delete a file from the bucket.

    Attributes:
        message -- An explanation of the error.
        filenames -- A list of files which could not be deleted.
        bucket -- The name of the bucket from which the files could not be deleted.
        minio_args -- The original minio errors.
    """
    def __init__(self, message: str, bucket: str, filenames: list[str], args) -> None:
        self.message = message
        self.bucket = bucket
        self.filenames = filenames
        self.minio_args = args

class MinioStorage:

    """A storage interface using Minio.

    Attributes:
      session -- The underlying minio client session.

    Methods:
        delete(name) -- Deletes from the object store by name.

        list(prefix, recursive) -- Lists objects (by name) relative to a given
            prefix. The `recursive` indicates whether we should list recursively
            into sub-directories.

        presigned_get(name, expires) -- Returns a presigned url for fetching
            `name` from the object store. The link will expire after a timedelta
            `expires`, or by default (when `expires==None`) the value of the
            `MINIO__DOWNLOAD_EXPIRE` environment variable (in seconds).

        presigned_put(name, expires) -- Returns a presigned url for putting
            an object on the store with name `name`. The link expires after a
            timedelta passed via `expires`, or by default it will expire after
            `MINIO__UPLOAD_EXPIRE` seconds.
    """

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

    def delete(self, names: list[str]) -> None:
        """Deletes stored objects"""
        errors = list(self.session.remove_objects(self._bucket, [DeleteObject(name) for name in names]))
        if (n_errors:=len(errors)) > 0:
            raise FileDeleteError(f"{n_errors} file(s) could not be deleted.", self._bucket, list(map(lambda e: e.name, errors)), errors)

    def list(self, prefix: str, recursive: bool = False) -> list[str]:
        """Lists objects (by name) relative to a given prefix"""
        return list(map(
            lambda o: o.object_name[prefix.rfind("/")+1:],
            self.session.list_objects(self._bucket, prefix, recursive=recursive)
        ))

    def put(self, name: str, data, size) -> None:
        """Uploads a file to Minio backend"""
        try:
            self.session.put_object(self._bucket, name, data, size)
        except ValueError as e:
            raise FilePutError("Could not upload file to storage backend", self._bucket, name, e.args)

    def presigned_get(self, object_name: str, file_name: str | None = None, expires: timedelta | None = None) -> str:
        """Creates a signed download url for the object"""
        if not expires:
            expires = self._download_expire
        extra_query_params = {}
        if file_name is not None and file_name != object_name:
            extra_query_params["response-content-disposition"] = f"attachment; filename=\"{file_name}\""

        return self.session.presigned_get_object(self._bucket, object_name, expires)

    def presigned_put(self, name: str, expires: timedelta | None = None) -> str:
        """Creates a signed upload url for the object"""
        if not expires:
            expires = self._upload_expire
        return self.session.presigned_put_object(self._bucket, name, expires)


storage = MinioStorage()
