# API Reference

Comprehensive REST API documentation for the Catalog Portfolio API service with detailed endpoint specifications, request/response schemas, and code examples.

## Authentication

All API endpoints require proper authentication. See the [Authentication](authentication.md) section for detailed information.

**Available Items:**

- [Brand Endpoints](brands.md) - Brand CRUD operations and search functionality

## Quick Reference

### Core Endpoints


  <i class="fas fa-download"></i> Download API Reference Template


| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/catalog/brands/ping` | Health check |
| `GET` | `/catalog/brands/search` | Search brands |
| `POST` | `/catalog/brands` | Create new brand |
| `GET` | `/catalog/brands/{brandId}` | Get brand by ID |
| `GET` | `/catalog/brands/{brandId}/allstatus` | Get brand with all status information |
| `PUT` | `/catalog/brands/{brandId}` | Update brand |
| `DELETE` | `/catalog/brands/{brandId}` | Delete brand |
| `PUT` | `/catalog/brands/{brandId}/activate` | Activate brand |
| `GET` | `/catalog/brands/{brandId}/activable` | Check if brand can be activated |
| `DELETE` | `/catalog/brands/{brandId}/tags/{tagName}` | Delete brand tag |

### Logo Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/catalog/brands/{brandId}/logos` | Get brand logos |
| `POST` | `/catalog/brands/{brandId}/logos` | Upload brand logo |
| `PUT` | `/catalog/brands/{brandId}/logos/{logoId}` | Update logo |
| `DELETE` | `/catalog/brands/{brandId}/logos/{logoId}` | Delete logo |

### Collector Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/catalog/brands/{brandId}/collectors` | Get brand collectors |
| `POST` | `/catalog/brands/{brandId}/collectors` | Associate brand with collectors |
| `DELETE` | `/catalog/brands/{brandId}/collectors/{collectorId}` | Remove brand-collector association |

### Resource Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `PUT` | `/catalog/brands/{brandId}/resources` | Create or update brand resources |

## Response Format

All API responses follow a consistent format:

```json
{
  "data": {
    // Response payload
  },
  "paging": {
    "total": 100,
    "offset": 0,
    "limit": 50
  },
  "status": 200
}
```

## Error Format

Error responses include detailed information:

```json
{
  "error": "brand_not_found",
  "message": "Brand with ID 123 was not found",
  "status": 404,
  "cause": []
}
```

## Rate Limiting

- **Rate Limit**: 1000 requests per minute per client
- **Headers**: `X-RateLimit-Limit`, `X-RateLimit-Remaining`

## Testing

Use the interactive [Swagger UI](https://web.flowcloudcloud.io/catalog-portfolio-api/specs-hub) for live API testing. 