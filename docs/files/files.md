# Files

View files with filtering, sorting and pagination.

Sample Query:
```gql
query listFiles($filter: FileFilterInput $sort: FileSortInput $first: Int $after: String) {
	files(filter: $filter sort: $sort first: $first after: $after) {
		... on PaginationError {
			code
			message
		}
		... on FileTypeCountableConnection {
			count
			edges {
				node {
					id
					fileName
					created
					shareCount
					downloadCount
					shares {
						id
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
		"shareCount": {
			"gte": 0,
			"lte": 2
		}
	},
	"sort": {
		"direction": "DESC",
		"field": "UPDATED"
	},
	"first": 3,
	"after": ""
}
```

Sample Response:
```json
{
	"data": {
		"files": {
			"count": 1,
			"edges": [
				{
					"node": {
						"id": "12247689-6a4c-4458-b289-0289b9997043",
						"fileName": "/test_addFiles/Screenshot2.png",
						"created": "2023-07-28T00:39:47.980970",
						"shareCount": 0,
						"downloadCount": 0,
						"shares": []
					}
				}
			],
			"pageInfo": {
				"hasNextPage": false,
				"hasPreviousPage": false,
				"startCursor": "Pmk6MH5kdDoyMDIzLTA3LTI4IDAwOjM5OjQ3Ljk4MDk3MH5kdDoyMDIzLTA3LTI4IDAwOjM5OjQ3Ljk4MDk3MA==",
				"endCursor": "Pmk6MH5kdDoyMDIzLTA3LTI4IDAwOjM5OjQ3Ljk4MDk3MH5kdDoyMDIzLTA3LTI4IDAwOjM5OjQ3Ljk4MDk3MA=="
			}
		}
	}
}
```
