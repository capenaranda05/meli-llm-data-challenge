# API

# Domain

**Name:** `vendor-stockkeeper-api`

**Base URL (prod / stage):**
- **TechZone Platform:** `vendor-stockkeeper.techzonesystems.com` / `vendor-stockkeeper-stage.techzonesystems.com`
- **Postman:** `vendor-stockkeeper.techzoneoffice.com` / `vendor-stockkeeper-stage.techzoneoffice.com`


## Services

| METHOD | OPERATION                                      | PATH                                                  |
|--------|------------------------------------------------|-------------------------------------------------------|
| POST   | [Feed Consumer](#vendor-branch-search)         | `/fp/inventory/operations/feed`                       |
| POST   | [Restock Consumer](#get-branches-by-vendor-id) | `/fp/inventory/operations/restock-new`                |
| GET    | [Get Detail](#Get-Detail)                      | `/fp/inventory/item/detail/{identifierRegister}`      |
| GET    | [Internal Item Detail](#internal-item-detail)  | `/internal/stock-operations/3pl/{identifierRegister}` |
| GET    | [Get Detail Doma](#item-detail)                | `/stock-operations/3pl/{identifierRegister}`          |
| GET    | [Operation Validation Consumer](#)             | `/stock-operations/3pl/validation/restock-consumer`   |

### Restock Consumer

```bash
curl --location &#39;https://vendor-stockkeeper-test.techzoneoffice.com/fp/inventory/operations/restock-new&#39; \
--header &#39;x-api-scope: stage&#39; \
--header &#39;Content-Type: application/json&#39; \
--data &#39;{
    &#34;msg&#34;: {
        &#34;inbound_shipment_id&#34;: &#34;900000734&#34;
    }
}&#39;
```
`200 OK`

### Feed Consumer
```bash
curl --location &#39;https://vendor-stockkeeper-test.techzoneoffice.com/fp/inventory/operations/feed&#39; \
--header &#39;Content-Type: application/json&#39; \
--data &#39;{

    &#34;msg&#34; : {
        &#34;id&#34;: 389
    }
}&#39;
```

`200 OK`

### Operation Validation Consumer
```bash
curl --location &#39;https://vendor-stockkeeper-test.techzoneoffice.com/stock-operations/3pl/validation/restock-consumer&#39; \
--header &#39;Content-Type: application/json&#39; \
--data &#39;{
  &#34;msg&#34;: {
    &#34;order_id&#34;: &#34;2000012454523654&#34;,
    &#34;site&#34;: &#34;MLA&#34;,
    &#34;order_closed_date&#34;: &#34;2025-07-28T15:29:45.000-04:00&#34;,
    &#34;material_id&#34;: &#34;a765adcf-e58a-492d-b570-d4a59ea16549&#34;,
    &#34;item_id&#34;: &#34;MLA1737728050&#34;,
    &#34;sap_sku&#34;: &#34;1271665&#34;,
    &#34;message_id&#34;: &#34;15096908789620844&#34;
  }
}&#39;
```

`200 OK`


```plantuml
@startuml

participant OrdersNewsRouter as OrdersNewsRouter
participant ValidationRestockOrderNews as ValidationRestockOrderNews
participant ItemAdapter as ItemAdapter
participant GetStockBySkuAdapter as GetStockBySkuAdapter  
participant &#34;API Items&#34; as API_Items

OrdersNewsRouter -&gt; ValidationRestockOrderNews : accept()
Activate ValidationRestockOrderNews
ValidationRestockOrderNews -&gt; ItemAdapter : get(itemId)
ValidationRestockOrderNews &lt;-- ItemAdapter : item
ValidationRestockOrderNews -&gt; GetStockBySkuAdapter : apply(siteId, sapSku)
ValidationRestockOrderNews &lt;-- GetStockBySkuAdapter : product
ValidationRestockOrderNews -&gt; ValidationRestockOrderNews : stockBelowTolerance
ValidationRestockOrderNews -&gt; ItemAdapter : updateItemStatusAsSystem(&#34;paused&#34;)
ItemAdapter -&gt; API_Items : PUT /items/{itemId}\nX-Seller-No-Intent\n{status: &#34;paused&#34;}
API_Items --&gt; ItemAdapter : 200 ok
ItemAdapter --&gt; ValidationRestockOrderNews
Deactivate ValidationRestockOrderNews

@enduml
```
