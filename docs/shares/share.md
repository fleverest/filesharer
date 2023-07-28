# Get a share

Queries a share by ID or by unique key.


Sample Query:
```gql
query getFile($id: UUID $key: String) {
	share(id: $id key: $key) {
		... on ShareType {
			id
			key
			created
			updated
			downloadCount
			downloadLimit
		}
		... on ShareNotFoundError {
			code
			message
		}
	}
}
```

Variables:
```json
{
	"id": null,
	"key": "key2"
}
```

Sample Response:
```json
{
	"data": {
		"share": {
			"id": "7427558e-b7d4-4851-aca7-9d14298069f8",
			"key": "key2",
			"created": "2023-07-28T00:50:45.604500",
			"updated": "2023-07-28T00:50:45.604500",
			"downloadCount": 0,
			"downloadLimit": 20
		}
	}
}
```
