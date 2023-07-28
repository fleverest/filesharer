# Filesharer

This application provides an interface to S3 to assist users in sharing files from a private S3 bucket. The application can be used to create readable URLs (known as a "share") which can be safely shared with third parties. The share is essentially an alias for an S3 presigned URL with a very short expiry, thus adding the capability to limit the number of times a file is downloaded by a third party, to no facilitate distribution of sensitive documents.


## TODOs

* Edit files in-place, e.g. change the name of the file or disable it.
* Download a share: add an API endpoint which retrieves a presigned-url from S3 and increments the download-count. We should also track the source IP for the request, but this will require a new model to be specified.
* Allow for uploads directly to the S3 backend. This would circumvent the necessary multi-part upload in the `add_files` mutation. We could have an api endpoint which created a presigned upload url with S3, allowing for direct uploads to the bucket with prespecified object names.
* Add one-time upload keys, like a share but in reverse.
