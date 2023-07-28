# Application Health Check

Users can issue a health check request to the Application

Query format:
```gql
query {
  ping
}
```

Response format:
```json
{
	"data": {
		"ping": "pong"
	}
}
```
