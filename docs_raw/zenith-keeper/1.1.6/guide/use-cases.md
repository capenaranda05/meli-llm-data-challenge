#Use cases

Fresh products API documentation - sequence diagrams


POST /fresh-products/inboundorder
```mermaid
    sequenceDiagram
        participant M as Manager
        participant C as FreshProductsController
        participant S as BatchOrderService
        participant R as OrderRepository
        participant D as Database
    
        M->>C: POST /inboundorder
        C-->>S: addNewBatchOfProducts(order)
        S->>R: save(newOrder)
        R->>D: insert(order)
        D-->>R: void
        R-->>S: void
        alt Inbound Order
            S-->>C: true
            C-->>M: HTTP 201
        else
            S-->>C: OrderAlreadyExistsException
            C-->>M: HTTP 404
        else
            S-->>C: InvalidSectionException
            C-->>M: HTTP 404
        else
            S-->>C: BatchQuantityExceedsSectionQuatityException
            C-->>M: HTTP 404
        end
```

PUT /fresh-products/inboundorder
```mermaid
    sequenceDiagram
        participant M as Manager
        participant C as FreshProductsController
        participant S as BatchOrderService
        participant R as OrderRepository
        participant D as Database
    
        M->>C: PUT /inboundorder
        C-->>S: updateBatchOfProducts(order)
        S->>R: save(newOrder)
        R->>D: insert(order)
        D-->>R: void
        R-->>S: void
        alt Inbound Order
            S-->>C: true
            C-->>M: HTTP 201
        else
            S-->>C: OrderNotExistException
            C-->>M: HTTP 404
        else
            S-->>C: InvalidSectionException
            C-->>M: HTTP 404
        else
            S-->>C: BatchQuantityExceedsSectionQuatityException
            C-->>M: HTTP 404
        end
```

GET /fresh-products
```mermaid
    sequenceDiagram
        participant M as Manager
        participant C as FreshProductsController
        participant S as PurchaseOrderService
        participant R as ProductRepository
        participant D as Database
    
        M->>C: GET /fresh-products
        C-->>S: getProductList()
        S->>R: findAllInStock()
        R->>D: select(products)
        D-->>R: List<Product>
        R-->>S: List<Product>
        alt List Products
            S-->>C: List<ProductDTO>
            C-->>M: HTTP 200 - List<ProductDTO>
        else
            S-->>C: ProductListEmptyException
            C-->>M: HTTP 404
        end 
```

GET /fresh-products/list-category{category}
```mermaid
    sequenceDiagram
        participant M as Manager
        participant C as FreshProductsController
        participant S as PurchaseOrderService
        participant R1 as ProductRepository
        participant R2 as ProductTypesRepository
        participant D as Database
    
        M->>C: GET /fresh-products/list-category{category}
        C->>S: getProductListForCategory(category)
        S->>R1: findByCategoryInStock(category)
        R1->>D: select(products)
        D-->>R1: List<Product>
        R1-->>S: List<Product>
        S->>R2: findById(category)
        R2->>D: select(category)
        D-->>R2: ProductTypes
        R2-->>S: ProductTypes

        alt List Products
            S-->>C: List<ProductDTO>
            C-->>M: HTTP 200 - List<ProductDTO>
        else
            S-->>C: ProductTypeNotFoundException
            C-->>M: HTTP 404
        else
            S-->>C: ProductListEmptyException
            C-->>M: HTTP 404
        end
```

POST /orders
```mermaid
    sequenceDiagram
        participant M as Manager
        participant C as FreshProductsController
        participant S as PurchaseOrderService
        participant R as ProductRepository
        participant D as Database
    
        M->>C: POST /orders
        C->>S: saveNewProductListOrder(order)
        S->>R: purchaseOrder
        R->>D: insert(purchaseOrder)
        D-->>R: true
        R-->>S: true

        alt Order
            S-->>C: PricePurchaseOrderDTO
            C-->>M: HTTP 201 - PricePurchaseOrderDTO
        else
            S-->>C: ProductsWithoutStockException
            C-->>M: HTTP 404
        else
            S-->>C: WarehousesWithoutStockException
            C-->>M: HTTP 404
        end
```

GET /orders
```mermaid
    sequenceDiagram
        participant M as Manager
        participant C as FreshProductsController
        participant S as PurchaseOrderService
        participant R as ProductRepository
        participant D as Database
    
        M->>C: GET /orders{idOrder}
        C->>S: getProductListOrder(idOrder)
        S->>R: findProductsByOrderId(idOrder)
        R->>D: select(product)
        D-->>R: List<Product>
        R-->>S: List<Product>

        alt Order
            S-->>C: List<ProductDTO>
            C-->>M: HTTP 201 - List<ProductDTO>
        else
            S-->>C: PurchaseOrderNotExistException
            C-->>M: HTTP 404
        end
```

PUT /orders

```mermaid
    sequenceDiagram
        participant M as Manager
        participant C as FreshProductsController
        participant S as PurchaseOrderService
        participant R as ProductRepository
        participant D as Database
    
        M->>C: PUT /orders{idOrder}
        C->>S: updateProductListOrder(idOrder, order)
        S->>R: purchaseOrder
        R->>D: update(purchaseOrder)
        D-->>R: true
        R-->>S: true

        alt Order
            S-->>C: PricePurchaseOrderDTO
            C-->>M: HTTP 201 - PricePurchaseOrderDTO
        else
            S-->>C: ProductsWithoutStockException
            C-->>M: HTTP 404
        else
            S-->>C: WarehousesWithoutStockException
            C-->>M: HTTP 404
        else
            S-->>C: PurchaseOrderNotExistException
            C-->>M: HTTP 404
        end
```

GET /fresh-products/list{productId}
```mermaid
    sequenceDiagram
        participant M as Manager
        participant C as FreshProductsController
        participant S as BatchOrderService
        participant R as BatchRepository
        participant D as Database
    
        M->>C: GET /fresh-products/list{productId}
        C->>S: findBatchsOfProduct(productId)
        S->>R: findBatchsByProductId(prodId)
        R->>D: select(batchs)
        D-->>R: List<Batch>
        R-->>S: List<Batch>

        alt Products List
            S-->>C: ProductBatchsResponseDTO
            C-->>M: HTTP 200 - ProductBatchsResponseDTO
        else
            S-->>C: ProductNotFoundException
            C-->>M: HTTP 404
        else
            S-->>C: ProductNotHaveBatchException
            C-->>M: HTTP 404
        end
```

GET /fresh-products/list/{productId}/{sort}
```mermaid
    sequenceDiagram
        participant M as Manager
        participant C as FreshProductsController
        participant S as BatchOrderService
        participant R as BatchRepository
        participant D as Database
    
        M->>C: GET /fresh-products/list/{productId}/{sort}
        C->>S: findBatchsOfProduct(productId, sort)
        S->>R: findBatchsByProductIdOrderBy{sort}(prodId)
        R->>D: select(batchs)
        D-->>R: List<Batch>
        R-->>S: List<Batch>

        alt Products List
            S-->>C: ProductBatchsResponseDTO
            C-->>M: HTTP 200 - ProductBatchsResponseDTO
        else
            S-->>C: ProductNotFoundException
            C-->>M: HTTP 404
        else
            S-->>C: ProductNotHaveBatchException
            C-->>M: HTTP 404
        end
```

GET /warehouse{productId}
```mermaid
    sequenceDiagram
        participant M as Manager
        participant C as FreshProductsController
        participant S as BatchOrderService
        participant R as BatchRepository
        participant D as Database
    
        M->>C: GET /warehouse/{productId}
        C->>S: findQuantityOfProduct(productId)
        S->>R: findBatchsByProductId(productId)
        R->>D: select(batchs)
        D-->>R: List<Batch>
        R-->>S: List<Batch>

        alt Products List
            S-->>C: ProductQuantityDTOResp
            C-->>M: HTTP 200 - ProductQuantityDTOResp
        else
            S-->>C: ProductNotFoundException
            C-->>M: HTTP 404
        else
            S-->>C: ProductNotHaveBatchException
            C-->>M: HTTP 404
        end
```

GET /due-date/{quantityOfDays}
```mermaid
    sequenceDiagram
        participant M as Manager
        participant C as FreshProductsController
        participant S as BatchOrderService
        participant R as BatchRepository
        participant D as Database
    
        M->>C: GET /due-date/{quantityOfDays}
        C->>S: findAllBatchsByDueDate(quantityOfDays)
        S->>R: findBatchByDueDateBetweenOrderBySectionSectionCode()
        R->>D: select(batchs)
        D-->>R: List<Batch>
        R-->>S: List<Batch>

        alt Due Date List
            S-->>C: BatchStockDTOResp
            C-->>M: HTTP 200 - BatchStockDTOResp
        end
```

GET /due-date/list{quantityOfDays}/{category}/{sort}
```mermaid
    sequenceDiagram
        participant M as Manager
        participant C as FreshProductsController
        participant S as BatchOrderService
        participant R as BatchRepository
        participant D as Database
    
        M->>C: GET /due-date/list{quantityOfDays}/{category}
        C->>S: findAllBatchsBySection(quatintyOfDays, category)
        S->>R: findBatchBySectionSectionCodeAndDueDateBetween()
        R->>D: select(batchs)
        D-->>R: List<Batch>
        R-->>S: List<Batch>

        alt Due Date List
            S-->>C: BatchStockDTOResp
            C-->>M: HTTP 200 - BatchStockDTOResp
        end
```