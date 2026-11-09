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
curl --location &#39;https://1p-inbounds-stage.techzoneoffice.com/inbounds/900000734/conciliations?scope=stage&#39;
```

<details>
<summary>Response Inbound conciliation</summary>

```json
{
  &#34;received&#34;: [
    {
      &#34;id&#34;: 250565042,
      &#34;was_declared&#34;: true,
      &#34;inbound_shipment_id&#34;: 900000734,
      &#34;purchase_order_id&#34;: &#34;0a9a21e0-aef7-48c7-9687-6515423d7638&#34;,
      &#34;material_id&#34;: &#34;02c8df4d-b4ca-416f-b8ba-8b4b444e45cb&#34;,
      &#34;item_id&#34;: &#34;MLA1734160848&#34;,
      &#34;inventory_id&#34;: &#34;EP1982710&#34;,
      &#34;sap_sku&#34;: &#34;930560&#34;,
      &#34;ean&#34;: &#34;7798118961384&#34;,
      &#34;status&#34;: &#34;ok&#34;,
      &#34;quantity&#34;: 1000,
      &#34;type&#34;: &#34;RECEIVED&#34;,
      &#34;deleted&#34;: false,
      &#34;date_created&#34;: &#34;2024-09-12&#34;,
      &#34;date_last_updated&#34;: &#34;2024-09-12&#34;,
      &#34;conciliation_criteria&#34;: &#34;OLDER_PO&#34;
    },
    {
      &#34;id&#34;: 250565044,
      &#34;was_declared&#34;: true,
      &#34;inbound_shipment_id&#34;: 900000734,
      &#34;purchase_order_id&#34;: &#34;0a9a21e0-aef7-48c7-9687-6515423d7638&#34;,
      &#34;material_id&#34;: &#34;6a60044d-cf2f-4f84-8b79-1e805e6b3930&#34;,
      &#34;item_id&#34;: &#34;MLA1734238432&#34;,
      &#34;inventory_id&#34;: &#34;EP1982711&#34;,
      &#34;sap_sku&#34;: &#34;930415&#34;,
      &#34;ean&#34;: &#34;7793862009900&#34;,
      &#34;status&#34;: &#34;ok&#34;,
      &#34;quantity&#34;: 1000,
      &#34;type&#34;: &#34;RECEIVED&#34;,
      &#34;deleted&#34;: false,
      &#34;date_created&#34;: &#34;2024-09-12&#34;,
      &#34;date_last_updated&#34;: &#34;2024-09-12&#34;,
      &#34;conciliation_criteria&#34;: &#34;OLDER_PO&#34;
    }
  ],
  &#34;declared&#34;: [
    {
      &#34;id&#34;: 250565041,
      &#34;inbound_shipment_id&#34;: 900000734,
      &#34;purchase_order_id&#34;: &#34;0a9a21e0-aef7-48c7-9687-6515423d7638&#34;,
      &#34;material_id&#34;: &#34;02c8df4d-b4ca-416f-b8ba-8b4b444e45cb&#34;,
      &#34;item_id&#34;: &#34;MLA1734160848&#34;,
      &#34;inventory_id&#34;: &#34;EP1982710&#34;,
      &#34;sap_sku&#34;: &#34;930560&#34;,
      &#34;ean&#34;: &#34;7798118961384&#34;,
      &#34;status&#34;: &#34;closed_ok&#34;,
      &#34;quantity&#34;: 1000,
      &#34;type&#34;: &#34;DECLARED&#34;,
      &#34;deleted&#34;: false,
      &#34;date_created&#34;: &#34;2024-09-12&#34;,
      &#34;date_last_updated&#34;: &#34;2024-09-12&#34;,
      &#34;conciliation_criteria&#34;: &#34;OLDER_PO&#34;
    },
    {
      &#34;id&#34;: 250565043,
      &#34;inbound_shipment_id&#34;: 900000734,
      &#34;purchase_order_id&#34;: &#34;0a9a21e0-aef7-48c7-9687-6515423d7638&#34;,
      &#34;material_id&#34;: &#34;6a60044d-cf2f-4f84-8b79-1e805e6b3930&#34;,
      &#34;item_id&#34;: &#34;MLA1734238432&#34;,
      &#34;inventory_id&#34;: &#34;EP1982711&#34;,
      &#34;sap_sku&#34;: &#34;930415&#34;,
      &#34;ean&#34;: &#34;7793862009900&#34;,
      &#34;status&#34;: &#34;closed_ok&#34;,
      &#34;quantity&#34;: 1000,
      &#34;type&#34;: &#34;DECLARED&#34;,
      &#34;deleted&#34;: false,
      &#34;date_created&#34;: &#34;2024-09-12&#34;,
      &#34;date_last_updated&#34;: &#34;2024-09-12&#34;,
      &#34;conciliation_criteria&#34;: &#34;OLDER_PO&#34;
    }
  ]
}
```

</details>

To identify that the items are test items, we must consult the item api and check their tags.

```bash
curl --location &#39;https://internal-api.techzone.com/items/MLA1737779958?caller.scopes=admin&amp;include_attributes=all
```

<details>
<summary>Response item details.</summary>

```json
{
   &#34;id&#34;: &#34;MLA0000000000&#34;,
   &#34;site_id&#34;: &#34;MLA&#34;,
   &#34;title&#34;: &#34;Producto Genérico&#34;,
   &#34;sanitized_title&#34;: &#34;producto-generico&#34;,
   &#34;family_name&#34;: null,
   &#34;subtitle&#34;: null,
   &#34;seller_id&#34;: 0,
   &#34;category_id&#34;: &#34;MLA0000&#34;,
   &#34;user_product_id&#34;: &#34;MLA000000000&#34;,
   &#34;official_store_id&#34;: null,
   &#34;price&#34;: 0.0,
   &#34;base_price&#34;: 0.0,
   &#34;original_price&#34;: null,
   &#34;inventory_id&#34;: &#34;DMED00000&#34;,
   &#34;currency_id&#34;: &#34;ARS&#34;,
   &#34;initial_quantity&#34;: 0,
   &#34;available_quantity&#34;: 0,
   &#34;sold_quantity&#34;: 0,
   &#34;sale_terms&#34;: [],
   &#34;buying_mode&#34;: &#34;buy_it_now&#34;,
   &#34;listing_type_id&#34;: &#34;gold_pro&#34;,
   &#34;start_time&#34;: &#34;2024-01-01T00:00:00.000Z&#34;,
   &#34;historical_start_time&#34;: &#34;2024-01-01T00:00:00.000Z&#34;,
   &#34;stop_time&#34;: &#34;2044-01-01T00:00:00.000Z&#34;,
   &#34;end_time&#34;: &#34;2044-01-01T00:00:00.000Z&#34;,
   &#34;expiration_time&#34;: &#34;2025-01-01T00:00:00.000Z&#34;,
   &#34;condition&#34;: &#34;new&#34;,
   &#34;permalink&#34;: &#34;https://articulo.techzone.com.ar/MLA-0000000000-producto-generico-_JM&#34;,
   &#34;thumbnail_id&#34;: &#34;000000-MLA0000000000_000000&#34;,
   &#34;thumbnail&#34;: &#34;https://default.thumbnail.url&#34;,
   &#34;secure_thumbnail&#34;: &#34;https://default.thumbnail.url&#34;,
   &#34;pictures&#34;: [],
   &#34;video_id&#34;: null,
   &#34;descriptions&#34;: [],
   &#34;accepts_techzone-payment&#34;: true,
   &#34;non_techzone_payment_payment_methods&#34;: [],
   &#34;shipping&#34;: {
      &#34;mode&#34;: &#34;me1&#34;,
      &#34;methods&#34;: [],
      &#34;tags&#34;: [],
      &#34;dimensions&#34;: &#34;0x0x0,0&#34;,
      &#34;local_pick_up&#34;: false,
      &#34;free_shipping&#34;: false,
      &#34;logistic_type&#34;: &#34;default&#34;,
      &#34;store_pick_up&#34;: false
   },
   &#34;international_delivery_mode&#34;: &#34;none&#34;,
   &#34;seller_address&#34;: {},
   &#34;seller_contact&#34;: null,
   &#34;location&#34;: {},
   &#34;geolocation&#34;: {
      &#34;latitude&#34;: null,
      &#34;longitude&#34;: null
   },
   &#34;coverage_areas&#34;: [],
   &#34;warnings&#34;: {},
   &#34;listing_source&#34;: {},
   &#34;variations&#34;: [],
   &#34;status&#34;: &#34;active&#34;,
   &#34;sub_status&#34;: {},
    &#34;tags&#34;: [
      &#34;good_quality_thumbnail&#34;,
      &#34;1p_24x_campaign&#34;,
      &#34;kvs_primary&#34;,
      &#34;test_item&#34;,
      &#34;immediate_payment&#34;,
      &#34;cart_eligible&#34;
    ],
   &#34;warranty&#34;: &#34;Garantía de fábrica: 12 meses&#34;,
   &#34;catalog_product_id&#34;: &#34;MLA00000000&#34;,
   &#34;domain_id&#34;: &#34;MLA-DEFAULT_DOMAIN&#34;,
   &#34;seller_custom_field&#34;: null,
   &#34;parent_item_id&#34;: null,
   &#34;differential_pricing&#34;: {},
   &#34;deal_ids&#34;: [],
   &#34;automatic_relist&#34;: false,
   &#34;date_created&#34;: &#34;2024-01-01T00:00:00.000Z&#34;,
   &#34;last_updated&#34;: &#34;2024-01-01T00:00:00.000Z&#34;,
   &#34;fee&#34;: 0,
   &#34;client_id&#34;: 0,
   &#34;sale_fee&#34;: 0.0,
   &#34;total_listing_fee&#34;: null,
   &#34;health&#34;: null,
   &#34;catalog_listing&#34;: true,
   &#34;item_relations&#34;: [],
   &#34;channels&#34;: [],
   &#34;bundle&#34;: {},
   &#34;availability&#34;: {}
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
{&#34;id&#34;:1909112490,&#34;location_id&#34;:&#34;BRSP02&#34;,&#34;process_name&#34;:&#34;packing&#34;,&#34;seller_product_id&#34;:&#34;MQWY26213&#34;,&#34;site_id&#34;:&#34;MLM&#34;,&#34;seller_id&#34;:&#34;123445&#34;,&#34;sap_sku&#34;:&#34;SAP1234434&#34;,&#34;date_created&#34;:&#34;2021-07-05T03:31:58Z&#34;,&#34;quantities&#34;:{&#34;available_quantity&#34;:1,&#34;not_available_quantity&#34;:0,&#34;not_available_details&#34;:[{&#34;status&#34;:&#34;damaged&#34;,&#34;quantity&#34;:1}]},&#34;external_references&#34;:{&#34;inbound_id&#34;:&#34;2610617&#34;,&#34;shipping_id&#34;:&#34;2610617&#34;,&#34;order_id&#34;:&#34;2610617&#34;,&#34;movement_name&#34;:&#34;NOT_DELIVERED_OK&#34;,&#34;movement_code&#34;:&#34;INV1NDOK&#34;}}
```

Which are: **[sap_sku, material_id, site_id, seller_id]**

These are used to query **materials** either by sap sku or material id.
sap sku or material id we obtain the item and with this we go to consult the items api
to be able to consult its tags and validate if it is a test item or not.

```bash
curl --location &#39;https://1p-materials.techzoneoffice.com/materials/facade/search?limit=100&amp;offset=0&#39; \
--header &#39;Content-Type: application/json&#39; \
--data &#39;{
  &#34;query&#34;: {
    &#34;and&#34;: [
      {
        &#34;in&#34;: {
          &#34;field&#34;: &#34;sap_sku&#34;,
          &#34;value&#34;: &#34;930588&#34;
        }
      },
      {
        &#34;eq&#34;: {
          &#34;field&#34;: &#34;site_id&#34;,
          &#34;value&#34;: &#34;MLA&#34;
        }
      }
    ]
  },
  &#34;projections&#34;: [
    &#34;id&#34;,
    &#34;sap_sku&#34;,
    &#34;site_id&#34;,
    &#34;items&#34;
  ]
}    &#39;
```
