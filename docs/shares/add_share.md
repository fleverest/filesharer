# Add shares

Add a public share url for a file.

Sample Mutation:
```gql
mutation($fileId: UUID! $key: String! $downloadLimit: Int $expiry: DateTime) {
	addShare(fileId: $fileId key: $key downloadLimit: $downloadLimit expiry: $expiry) {
		... on FileNotFoundError {
			code
			message
		}
		... on AddShareError {
			code
			message
		}
		... on ShareType {
			id
			key
			created
			updated
			downloadCount
			downloadLimit
			file {
				id
				fileName
				downloadCount
			}
		}
	}
}
```

Variables:
```json
{
	"fileId": "12247689-6a4c-4458-b289-0289b9997043",
	"key": "key2",
	"downloadLimit": 20,
	"expiry": "2023-07-29T02:19:38.786448"
}
```

Sample Response:
```json
{
	"data": {
		"addShare": {
			"id": "7427558e-b7d4-4851-aca7-9d14298069f8",
			"key": "key2",
			"created": "2023-07-28T00:50:45.604500",
			"updated": "2023-07-28T00:50:45.604500",
			"downloadCount": 0,
			"downloadLimit": 20,
			"file": {
				"id": "12247689-6a4c-4458-b289-0289b9997043",
				"fileName": "/test_addFiles/Screenshot2.png",
				"downloadCount": 0
			}
		}
	}
}
```
