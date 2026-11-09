# API

# Domain

**Name:** `vendor-stockkeeper-api`

**Base URL (prod / stage):**
- **TechZone Platform:** `vendor-stockkeeper.techzonesystems.com` / `vendor-stockkeeper-stage.techzonesystems.com`
- **Postman:** `vendor-stockkeeper.techzoneoffice.com` / `vendor-stockkeeper-stage.techzoneoffice.com`


## Services

| METHOD            | OPERATION                                                 | PATH                                      |
|-------------------|-----------------------------------------------------------|-------------------------------------------|
| POST              | [Feed Consumer](#vendor-branch-search)                   | `/fp/inventory/operations/feed`          |
| POST              | [Restock Consumer](#get-branches-by-vendor-id)           | `/fp/inventory/operations/restock-new`   |
| GET               | [Get Detail](#Get-Detail)                             | `/fp/inventory/item/detail/{identifierRegister}`     |
| GET               | [Internal Item Detail](#internal-item-detail)            | `/internal/stock-operations/3pl/{identifierRegister}`|
| GET               | [Get Detail Doma](#item-detail)                              | `/stock-operations/3pl/{identifierRegister}`         |

### Restock Consumer
<!-- tab:Operation -->
```bash
curl --location 'https://vendor-stockkeeper-test.techzoneoffice.com/fp/inventory/operations/restock-new' \
--header 'x-api-scope: stage' \
--header 'Content-Type: application/json' \
--data '{
    "msg": {
        "inbound_shipment_id": "900000734"
    }
}'
```
`200 OK`

### Feed Consumer
```bash
curl --location 'https://vendor-stockkeeper-test.techzoneoffice.com/fp/inventory/operations/feed' \
--header 'Content-Type: application/json' \
--data '{

    "msg" : {
        "id": 389
    }
}'
```

`200 OK`
