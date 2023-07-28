# Filesharer

This application provides an interface to S3 to assist users in sharing files from a private S3 bucket. The application can be used to create readable URLs (known as a "share") which can be safely shared with third parties. The share is essentially an alias for an S3 presigned URL with a very short expiry, thus adding the capability to limit the number of times a file is downloaded by a third party, to avoid facilitating direct distribution of sensitive documents.
