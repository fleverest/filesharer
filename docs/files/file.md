# File

View a single file by ID or by filename.

Sample Query:
```gql
query getFile($id: UUID!) {
	file(id: $id) {
		... on FileType {
			id
			fileName
			active
			created
			updated
			shares {
				id
			}
		}
		... on FileNotFoundError {
			code
			message
		}
	}
}
```

Variables:
```json
{
	"id": "12247689-6a4c-4458-b289-0289b9997043"
}
```

Sample Response:
```json
{
	"data": {
		"file": {
			"id": "12247689-6a4c-4458-b289-0289b9997043",
			"fileName": "/test_addFiles/Screenshot2.png",
			"active": true,
			"created": "2023-07-28T00:39:47.980970",
			"updated": "2023-07-28T00:39:47.980970",
			"shares": []
		}
	}
}
```
