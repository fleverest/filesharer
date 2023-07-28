# Add files

Uploads files to the storage backend and track them in the database. The request must be a Multipart Form as follows:

operations:
```json
{
	"query": "mutation($files: [Upload!]! $prefix: String!) {addFiles(prefix: $prefix files: $files) {added {id fileName created active} errors {code message}}}",
	"variables": {
	  "files": [null, null],
		"prefix": "/test_addFiles/"
	}
}
```

map:
```json
{
    "file1": ["variables.files.0"],
    "file2": ["variables.files.1"]
}
```

file1: `/path/to/Screenshot1.png`

file2: `/path/to/Screenshot2.png`


Further files can be uploaded by extending the `files` variable array and adding furhter file objects to the map and adding extra file parts to the form.


Sample response:
```json
{
	"data": {
		"addFiles": {
			"added": [
				{
					"id": "3247a435-dadf-43b0-a0f4-9906522e63da",
					"fileName": "/test_addFiles/Screenshot1.png",
					"created": "2023-07-14T07:32:09.315786",
					"active": true
				}
			],
			"errors": [
				{
					"code": "add_files_database_unique_violation_error",
					"message": "Could not add '/test_addFiles/Screenshot2.png': file already exists in database."
				}
			]
		}
	}
}
```
