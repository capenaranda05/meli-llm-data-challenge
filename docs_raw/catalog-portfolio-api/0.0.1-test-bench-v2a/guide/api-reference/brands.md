# Brand Endpoints

Complete reference for all brand-related API endpoints with request/response examples.

## Base URL

```
Production: https://api.mp.internal.retailflow.com/catalog/brands
Development: http://api.mp.internal.retailflow.com/catalog/brands
```


  <i class="fas fa-download"></i> Download Brand Endpoints Template


## Search Brands

Search for brands with various filters and pagination.

### `GET /`

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `collector_id` | integer | No | Filter by collector ID |
| `brand_name` | string | No | Filter by brand name |
| `site` | string | No | Filter by site (MLA, MLB, MLC, etc.) |
| `tag` | string | No | Filter by tag (can be used multiple times) |
| `owner_id` | integer | No | Filter by owner ID |
| `type` | string | No | Filter by type (lighthouse, standard) |
| `status` | string | No | Filter by status (ACTIVE, STAND_BY) |
| `offset` | integer | No | Number of items to skip (default: 0) |
| `limit` | integer | No | Number of items to return (default: 50, max: 200) |

**Example Request:**

```bash
curl "https://api.mp.internal.retailflow.com/catalog/brands/?site=MLA&status=ACTIVE&limit=10"
```

**Example Response:**

```json
{
  "results": [
    {
      "id": 2,
      "name": "McDonald's",
      "soft_descriptor": "MCDONALDS",
      "site": "MLB",
      "category": 5611201,
      "subcategories": [],
      "type": "lighthouse",
      "tags": ["611724878", "bf_mlb_2020"],
      "priority": 9,
      "status": "ACTIVE",
      "date_created": "2019-11-25T17:17:24.000-04:00",
      "date_last_updated": "2021-06-10T13:17:10.000-04:00"
    }
  ],
  "paging": {
    "total": 1,
    "offset": 0,
    "limit": 10
  }
}
```

## Create Brand

Create a new brand in the system.

### `POST /`

**Request Body:**

```json
{
  "name": "Example Brand",
  "soft_descriptor": "EXAMPLE",
  "site": "MLA",
  "category": 5611201,
  "subcategories": [123, 456],
  "type": "lighthouse",
  "tags": ["tag1", "tag2"],
  "priority": 5,
  "business_description": "Business description text"
}
```

**Required Fields:**
- `name`: Brand name (must be unique within site)
- `site`: RetailFlow site code
- `category`: Primary category ID
- `type`: Brand type (lighthouse or standard)

**Example Request:**

```bash
curl -X POST "https://api.mp.internal.retailflow.com/catalog/brands/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Example Brand",
    "site": "MLA",
    "category": 5611201,
    "type": "lighthouse"
  }'
```

**Example Response:**

```json
{
  "id": 123,
  "name": "Example Brand",
  "site": "MLA",
  "category": 5611201,
  "type": "lighthouse",
  "status": "STAND_BY",
  "date_created": "2024-01-15T10:30:00.000-03:00",
  "date_last_updated": "2024-01-15T10:30:00.000-03:00"
}
```

## Get Brand

Retrieve a specific brand by ID.

### `GET /{brandId}`

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `brandId` | integer | Yes | Brand ID |

**Example Request:**

```bash
curl "https://api.mp.internal.retailflow.com/catalog/brands/123"
```

**Example Response:**

```json
{
  "id": 123,
  "name": "Example Brand",
  "soft_descriptor": "EXAMPLE",
  "site": "MLA",
  "category": 5611201,
  "subcategories": [],
  "type": "lighthouse",
  "tags": [],
  "logos": [
    {
      "id": 456,
      "brand_id": 123,
      "type": "main",
      "picture_id": "ML123456789"
    }
  ],
  "resources": [],
  "priority": 5,
  "status": "STAND_BY",
  "date_created": "2024-01-15T10:30:00.000-03:00",
  "date_last_updated": "2024-01-15T10:30:00.000-03:00"
}
```

## Update Brand

Update an existing brand's information.

### `PUT /{brandId}`

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `brandId` | integer | Yes | Brand ID |

**Request Body:**

```json
{
  "name": "Updated Brand Name",
  "soft_descriptor": "UPDATED",
  "category": 5611201,
  "subcategories": [789],
  "tags": ["new_tag"],
  "priority": 8,
  "business_description": "Updated description"
}
```

**Example Request:**

```bash
curl -X PUT "https://api.mp.internal.retailflow.com/catalog/brands/123" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Brand Name",
    "priority": 8
  }'
```

## Delete Brand

Permanently delete a brand from the system.

### `DELETE /{brandId}`

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `brandId` | integer | Yes | Brand ID |

**Headers:**

| Header | Type | Required | Description |
|--------|------|----------|-------------|
| `X-Client-Id` | string | Yes | Client ID (must be whitelisted) |

**Example Request:**

```bash
curl -X DELETE "https://api.mp.internal.retailflow.com/catalog/brands/123" \
  -H "X-Client-Id: your-client-id"
```

**Example Response:**

```json
{
  "message": "Brand deleted successfully",
  "status": 200
}
```

## Activate Brand

Activate a brand after validation.

### `PUT /{brandId}/activate`

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `brandId` | integer | Yes | Brand ID |

**Example Request:**

```bash
curl -X PUT "https://api.mp.internal.retailflow.com/catalog/brands/123/activate"
```

**Example Response:**

```json
{
  "id": 123,
  "name": "Example Brand",
  "status": "ACTIVE",
  "date_last_updated": "2024-01-15T11:00:00.000-03:00"
}
```

## Check Brand Activable

Check if a brand can be activated.

### `GET /{brandId}/activable`

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `brandId` | integer | Yes | Brand ID |

**Example Request:**

```bash
curl "https://api.mp.internal.retailflow.com/catalog/brands/123/activable"
```

**Example Response:**

```json
{
  "valid": false,
  "validationDetails": [
    "Main logo is missing",
    "Category validation failed"
  ]
}
```

## Error Responses

### Common Error Codes

| Code | Error | Description |
|------|-------|-------------|
| 400 | `validation_error` | Request validation failed |
| 401 | `unauthorized` | Missing or invalid authentication |
| 403 | `forbidden` | Insufficient permissions |
| 404 | `brand_not_found` | Brand ID does not exist |
| 409 | `brand_name_already_exists` | Brand name already exists in site |
| 422 | `logos_missing` | Required logos not uploaded |
| 500 | `internal_server_error` | Internal server error |

### Error Response Format

```json
{
  "error": "brand_not_found",
  "message": "Brand with ID 123 was not found",
  "status": 404,
  "cause": []
}
```

## Rate Limiting

- **Limit**: 1000 requests per minute
- **Headers**: 
  - `X-RateLimit-Limit`: Maximum requests per window
  - `X-RateLimit-Remaining`: Remaining requests in current window
  - `X-RateLimit-Reset`: Window reset time 