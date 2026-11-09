# Verification of Items in Inventory Flows

## Introduction

Before executing any action on the inventory flows, it is crucial to ensure that both the inbound and outbound
movement contain all their test items. This check is fundamental to avoid affecting the item API and, therefore, the inventory.
API and, therefore, in the inventory.

## Inventory Flows

There are two main flows where this verification is necessary:

1. **Restock**
2. **Feed**

## Importance of Verification

- **Error Prevention**: Lack of test items can lead to inventory errors.
- **API Integrity**: Ensuring that the data sent to the item API is correct is essential to maintain the integrity of the system.
- **Avoiding Unwanted Alterations**: Incorrect movement can directly affect the inventory status, leading to discrepancies and operational problems.

## Verification Procedure

1. **Review the Inbound (Restock flow)**: Make sure that all test items are present.
2. **Check the Operation Id (Feed flow)**: Confirm that the operationId also contains all items required.
3. **Final Validation**: Before proceeding with any action, perform a final validation of both flows.

## Conclusion

Implementing this systematic verification is key to maintaining the integrity of the inventory and item API.
Be sure to follow these steps before executing any action on inventory flows.

## How can we do it?

### Restock Flow

Before we send any kind of inbound we must first get that inbound and go to inbound conciliation to check if the items have the tags that identify an item as a test item.


```bash
curl --location 'https://1p-inbounds-stage.techzoneoffice.com/inbounds/900000734/conciliations?scope=stage'
```

<details>
<summary style="border: 1px solid #ccc; padding: 10px; background-color: #f9f9f9; border-radius: 5px;">Response Inbound conciliation</summary>

```json
{
  "received": [
    {
      "id": 250565042,
      "was_declared": true,
      "inbound_shipment_id": 900000734,
      "purchase_order_id": "0a9a21e0-aef7-48c7-9687-6515423d7638",
      "material_id": "02c8df4d-b4ca-416f-b8ba-8b4b444e45cb",
      "item_id": "MLA1734160848",
      "inventory_id": "EP1982710",
      "sap_sku": "930560",
      "ean": "7798118961384",
      "status": "ok",
      "quantity": 1000,
      "type": "RECEIVED",
      "deleted": false,
      "date_created": "2024-09-12",
      "date_last_updated": "2024-09-12",
      "conciliation_criteria": "OLDER_PO"
    },
    {
      "id": 250565044,
      "was_declared": true,
      "inbound_shipment_id": 900000734,
      "purchase_order_id": "0a9a21e0-aef7-48c7-9687-6515423d7638",
      "material_id": "6a60044d-cf2f-4f84-8b79-1e805e6b3930",
      "item_id": "MLA1734238432",
      "inventory_id": "EP1982711",
      "sap_sku": "930415",
      "ean": "7793862009900",
      "status": "ok",
      "quantity": 1000,
      "type": "RECEIVED",
      "deleted": false,
      "date_created": "2024-09-12",
      "date_last_updated": "2024-09-12",
      "conciliation_criteria": "OLDER_PO"
    }
  ],
  "declared": [
    {
      "id": 250565041,
      "inbound_shipment_id": 900000734,
      "purchase_order_id": "0a9a21e0-aef7-48c7-9687-6515423d7638",
      "material_id": "02c8df4d-b4ca-416f-b8ba-8b4b444e45cb",
      "item_id": "MLA1734160848",
      "inventory_id": "EP1982710",
      "sap_sku": "930560",
      "ean": "7798118961384",
      "status": "closed_ok",
      "quantity": 1000,
      "type": "DECLARED",
      "deleted": false,
      "date_created": "2024-09-12",
      "date_last_updated": "2024-09-12",
      "conciliation_criteria": "OLDER_PO"
    },
    {
      "id": 250565043,
      "inbound_shipment_id": 900000734,
      "purchase_order_id": "0a9a21e0-aef7-48c7-9687-6515423d7638",
      "material_id": "6a60044d-cf2f-4f84-8b79-1e805e6b3930",
      "item_id": "MLA1734238432",
      "inventory_id": "EP1982711",
      "sap_sku": "930415",
      "ean": "7793862009900",
      "status": "closed_ok",
      "quantity": 1000,
      "type": "DECLARED",
      "deleted": false,
      "date_created": "2024-09-12",
      "date_last_updated": "2024-09-12",
      "conciliation_criteria": "OLDER_PO"
    }
  ]
}
```

</details>

To identify that the items are test items, we must consult the item api and check their tags.

```bash
curl --location 'https://internal-api.techzone.com/items/MLA1737779958?caller.scopes=admin&include_attributes=all
```

<details>
<summary style="border: 1px solid #ccc; padding: 10px; background-color: #f9f9f9; border-radius: 5px;">Response item details.</summary>

```json
{
   "id": "MLA0000000000",
   "site_id": "MLA",
   "title": "Producto Genérico",
   "sanitized_title": "producto-generico",
   "family_name": null,
   "subtitle": null,
   "seller_id": 0,
   "category_id": "MLA0000",
   "user_product_id": "MLA000000000",
   "official_store_id": null,
   "price": 0.0,
   "base_price": 0.0,
   "original_price": null,
   "inventory_id": "DMED00000",
   "currency_id": "ARS",
   "initial_quantity": 0,
   "available_quantity": 0,
   "sold_quantity": 0,
   "sale_terms": [],
   "buying_mode": "buy_it_now",
   "listing_type_id": "gold_pro",
   "start_time": "2024-01-01T00:00:00.000Z",
   "historical_start_time": "2024-01-01T00:00:00.000Z",
   "stop_time": "2044-01-01T00:00:00.000Z",
   "end_time": "2044-01-01T00:00:00.000Z",
   "expiration_time": "2025-01-01T00:00:00.000Z",
   "condition": "new",
   "permalink": "https://articulo.techzone.com.ar/MLA-0000000000-producto-generico-_JM",
   "thumbnail_id": "000000-MLA0000000000_000000",
   "thumbnail": "https://default.thumbnail.url",
   "secure_thumbnail": "https://default.thumbnail.url",
   "pictures": [],
   "video_id": null,
   "descriptions": [],
   "accepts_techzone-payment": true,
   "non_techzone_payment_payment_methods": [],
   "shipping": {
      "mode": "me1",
      "methods": [],
      "tags": [],
      "dimensions": "0x0x0,0",
      "local_pick_up": false,
      "free_shipping": false,
      "logistic_type": "default",
      "store_pick_up": false
   },
   "international_delivery_mode": "none",
   "seller_address": {},
   "seller_contact": null,
   "location": {},
   "geolocation": {
      "latitude": null,
      "longitude": null
   },
   "coverage_areas": [],
   "warnings": {},
   "listing_source": {},
   "variations": [],
   "status": "active",
   "sub_status": {},
    "tags": [
      "good_quality_thumbnail",
      "1p_24x_campaign",
      "kvs_primary",
      "test_item",
      "immediate_payment",
      "cart_eligible"
    ],
   "warranty": "Garantía de fábrica: 12 meses",
   "catalog_product_id": "MLA00000000",
   "domain_id": "MLA-DEFAULT_DOMAIN",
   "seller_custom_field": null,
   "parent_item_id": null,
   "differential_pricing": {},
   "deal_ids": [],
   "automatic_relist": false,
   "date_created": "2024-01-01T00:00:00.000Z",
   "last_updated": "2024-01-01T00:00:00.000Z",
   "fee": 0,
   "client_id": 0,
   "sale_fee": 0.0,
   "total_listing_fee": null,
   "health": null,
   "catalog_listing": true,
   "item_relations": [],
   "channels": [],
   "bundle": {},
   "availability": {}
}
```
</details>

To identify that an item is a test item, we must check its **tags** and check that it has **test_items** or any of the tags that identify that an item is a test item.
tags that identify that an item is a test item.

![img.png](assets/images/img.png)


### Feed Flow

This Flow has an **Operation id** with this one we must query the database of
1p-3pl-integrator called 1p_3pl_product_stock_mov

![img_1.png](assets/images/img_1.png)


in this table we obtain key data to be able to consult if the items are test items or not.
``` json
{"id":1909112490,"location_id":"BRSP02","process_name":"packing","seller_product_id":"MQWY26213","site_id":"MLM","seller_id":"123445","sap_sku":"SAP1234434","date_created":"2021-07-05T03:31:58Z","quantities":{"available_quantity":1,"not_available_quantity":0,"not_available_details":[{"status":"damaged","quantity":1}]},"external_references":{"inbound_id":"2610617","shipping_id":"2610617","order_id":"2610617","movement_name":"NOT_DELIVERED_OK","movement_code":"INV1NDOK"}}
```

Which are: **[sap_sku, material_id, site_id, seller_id]**

These are used to query **materials** either by sap sku or material id.
sap sku or material id we obtain the item and with this we go to consult the items api
to be able to consult its tags and validate if it is a test item or not.

```bash
curl --location 'https://1p-materials.techzoneoffice.com/materials/facade/search?limit=100&offset=0' \
--header 'Content-Type: application/json' \
--data '{
  "query": {
    "and": [
      {
        "in": {
          "field": "sap_sku",
          "value": "930588"
        }
      },
      {
        "eq": {
          "field": "site_id",
          "value": "MLA"
        }
      }
    ]
  },
  "projections": [
    "id",
    "sap_sku",
    "site_id",
    "items"
  ]
}    '
```
