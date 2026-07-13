# Entity-Relationship Diagram — SwiftDash Database

## Schema Diagram (Mermaid)

```mermaid
erDiagram
    CUSTOMERS ||--o{ ORDERS : places
    RESTAURANTS ||--o{ ORDERS : receives
    DRIVERS ||--o{ ORDERS : delivers
    ORDERS ||--o{ ORDER_ITEMS : contains
    ORDERS ||--o| DELIVERY_LOGS : logs

    CUSTOMERS {
        varchar customer_id PK
        varchar name
        int age
        enum gender
        varchar city
        decimal latitude
        decimal longitude
        varchar phone
        varchar email
        date signup_date
        bool is_active
    }

    RESTAURANTS {
        varchar restaurant_id PK
        varchar name
        varchar cuisine_type
        varchar city
        decimal latitude
        decimal longitude
        decimal rating
        int avg_cost_for_two
        date join_date
        bool is_active
        int preparation_time_mins
    }

    DRIVERS {
        varchar driver_id PK
        varchar name
        int age
        varchar city
        decimal latitude
        decimal longitude
        enum vehicle_type
        decimal rating
        date join_date
        bool is_active
    }

    ORDERS {
        varchar order_id PK
        varchar customer_id FK
        varchar restaurant_id FK
        varchar driver_id FK
        datetime order_datetime
        date order_date
        tinyint order_hour
        varchar weekday
        bool is_weekend
        decimal order_amount
        decimal delivery_fee
        decimal discount
        decimal tax
        decimal platform_fee
        decimal surge_multiplier
        decimal total_amount
        enum payment_method
        enum order_status
        varchar customer_city
        varchar restaurant_city
        tinyint customer_rating
    }

    ORDER_ITEMS {
        int order_item_id PK
        varchar order_id FK
        varchar item_name
        varchar category
        int quantity
        decimal unit_price
        decimal line_total
    }

    DELIVERY_LOGS {
        varchar delivery_id PK
        varchar order_id FK
        varchar driver_id FK
        datetime pickup_datetime
        datetime drop_datetime
        decimal distance_km
        int travel_time_mins
        enum traffic_condition
        enum weather_condition
        bool is_on_time
    }
```

## Relationship Summary

| Parent | Child | Relationship Type | Description |
|--------|-------|------------------|-------------|
| `customers` | `orders` | One-to-Many | A customer can place many orders |
| `restaurants` | `orders` | One-to-Many | A restaurant can receive many orders |
| `drivers` | `orders` | One-to-Many | A driver can fulfill many orders |
| `orders` | `order_items` | One-to-Many | An order contains multiple items |
| `orders` | `delivery_logs` | One-to-One | Each delivered order has one delivery log |

## Key Design Decisions

1. **Central fact table:** `orders` sits at the center connecting customers, restaurants, and drivers — enabling multi-dimensional analysis in a single JOIN.

2. **Denormalized city fields:** `customer_city` and `restaurant_city` in the `orders` table avoid extra JOINs for city-level aggregations (a common analytics optimization).

3. **Delivery logs as separate table:** Rather than adding delivery fields to `orders`, a separate `delivery_logs` table keeps operational data distinct from transactional data. This also allows for one-to-one mapping (one delivery log per delivered order).

4. **Surge multiplier stored per order:** Captures the actual surge applied at order time, enabling "what-if" revenue analysis (revenue with and without surge).

5. **Nullable driver_id:** When an order is cancelled, no driver is assigned, so the FK is nullable.

6. **Indexes on high-query columns:** `order_date`, `customer_id`, `restaurant_id`, `order_status`, and `payment_method` are indexed for frequent WHERE and JOIN clauses.
