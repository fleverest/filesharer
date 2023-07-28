# Edit a share

Updates the parameters of a share, e.g. the expiry, download limit or its' key.

Sample Mutation:
```gql
mutation($id: UUID $key: String $newKey: String $newExpiry: DateTime $newDownloadLimit: Int) {
	editShare(key: $key id: $id newKey: $newKey newExpiry: $newExpiry newDownloadLimit: $newDownloadLimit) {
		... on ShareType {
			key
			expiry
			downloadCount
			downloadLimit
			file {
				fileName
			}
		}
		... on EditShareError {
			code
			message
		}
	}
}
```

Variables:
```json
{
	"key": "key1",
	"newKey": "key3"
}
```

Sample Response:
```json
{
	"data": {
		"editShare": {
			"key": "key3",
			"expiry": "2023-07-29T02:19:38.786448",
			"downloadCount": 0,
			"downloadLimit": 20,
			"file": {
				"fileName": "/test_addFiles/Screenshot2.png"
			}
		}
	}
}
```
