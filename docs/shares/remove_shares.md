# Remove shares

Deletes shares from the database, making them inaccessible.

Sample Mutation:
```gql
mutation($ids: [UUID!] $keys: [String!]) {
	removeShares(keys: $keys ids: $ids) {
		removed {
			key
			file {
				fileName
			}
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
	"keys": [
		"key1",
		"key2",
		"key3",
		"key4"
	],
	"ids": null
}
```

Sample Response:
```json
{
	"data": {
		"removeShares": {
			"removed": [
				{
					"key": "key2",
					"file": {
						"fileName": "/test_addFiles/Screenshot from 2023-01-12 10-37-01.png"
					}
				},
				{
					"key": "key3",
					"file": {
						"fileName": "/test_addFiles/Screenshot from 2023-01-12 10-37-01.png"
					}
				}
			],
			"errors": []
		}
	}
}
```
