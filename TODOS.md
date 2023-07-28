## TODOs

* Add authentication. It's basically useless without authentication.
* Edit files in-place, e.g. change the name of the file or disable it.
* Download a share: add an API endpoint which retrieves a presigned-url from S3 and increments the download-count. We should also track the source IP for the request, but this will require a new model to be specified.
* Allow for uploads directly to the S3 backend. This would circumvent the necessary multi-part upload in the `add_files` mutation. We could have an api endpoint which created a presigned upload url with S3, allowing for direct uploads to the bucket with prespecified object names.
* Add one-time upload keys, like a share but in reverse.
* Add migrations for changes to the database schema using [Alembic](https://alembic.sqlalchemy.org/en/latest/).
