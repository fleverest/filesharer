# List shares

Lists shares with filtering and sorting.

Sample Query:
```gql
query listShares($filter: ShareFilterInput $sort: ShareSortInput) {
	shares(filter: $filter sort: $sort first:50) {
		... on PaginationError {
			code
			message
		}
		... on ShareTypeCountableConnection {
			count
			edges {
				node {
					key
					created
					expiry
					downloadCount
					downloadLimit
					file {
						fileName
					}
				}
			}
			pageInfo {
				hasNextPage
				hasPreviousPage
				startCursor
				endCursor
			}
		}
	}
}
```

Variables:
```json
{
	"filter": {
		"downloadCount": {
			"gte": 0,
			"lte": 1
		}
	},
	"sort": {
		"direction": "DESC",
		"field": "CREATED"
	}
}
```

Sample Response:
```json
{
	"data": {
		"shares": {
			"count": 2,
			"edges": [
				{
					"node": {
						"key": "key2",
						"created": "2023-07-28T00:50:45.604500",
						"expiry": "2023-07-29T02:19:38.786448",
						"downloadCount": 0,
						"downloadLimit": 20,
						"file": {
							"fileName": "/test_addFiles/Screenshot2.png"
						}
					}
				},
				{
					"node": {
						"key": "key1",
						"created": "2023-07-28T00:49:59.331035",
						"expiry": "2023-07-29T02:19:38.786448",
						"downloadCount": 0,
						"downloadLimit": 20,
						"file": {
							"fileName": "/test_addFiles/Screenshot2.png"
						}
					}
				}
			],
			"pageInfo": {
				"hasNextPage": false,
				"hasPreviousPage": false,
				"startCursor": "Pmk6MH5kdDoyMDIzLTA3LTI4IDAwOjUwOjQ1LjYwNDUwMH5kdDoyMDIzLTA3LTI4IDAwOjUwOjQ1LjYwNDUwMA==",
				"endCursor": "Pmk6MH5kdDoyMDIzLTA3LTI4IDAwOjQ5OjU5LjMzMTAzNX5kdDoyMDIzLTA3LTI4IDAwOjQ5OjU5LjMzMTAzNQ=="
			}
		}
	}
}
```
