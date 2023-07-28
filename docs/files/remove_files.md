# Remove files

Removes files from the storage backend and from the database.

Sample Mutation:
```gql
mutation($filenames: [String!] $prefix: String! $ids: [UUID!]) {
	removeFiles(prefix: $prefix filenames: $filenames ids: $ids) {
		removed {
			id
			fileName
		}
		errors {
			code
			message
		}
	}
}
```
Variables:
```json
{
	"ids": [
		"d69b0b22-8f04-46ae-8f0a-bfecfc2e54a9",
        "3247a435-dadf-43b0-a0f4-9906522e63da"
	],
	"prefix": "/test_addFiles/"
}
```


Sample Response:
```json
{
	"data": {
		"removeFiles": {
			"removed": [
				{
					"id": "3247a435-dadf-43b0-a0f4-9906522e63da",
					"fileName": "/test_addFiles/Screenshot1.png"
				}
			],
			"errors": [
				{
					"code": "remove_files_file_not_found",
					"message": "Could not remove file by id 'd69b0b22-8f04-46ae-8f0a-bfecfc2e54a9': file not found.'"
				}
			]
		}
	}
}
```
