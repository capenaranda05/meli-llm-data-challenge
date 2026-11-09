# rule_row Table

The `rule_row` table stores , receiving data from PME.

The table has the following columns:

| Field          | Type   | Constraints | Description                | Extra                      |
|----------------|--------|-------------|----------------------------|----------------------------|
| id             | bigint | Not null    | Auto-increment primary key |                            |
| rule_id        | bigint | Not null    | Foreign                    | REFERENCES rule_header(id) |
| site_id        | json   | Null        | Sites Ids                  |                            |
| seller_id      | json   | Null        | Sellers Ids                |                            |
| domain         | json   | Null        | Domains                    |                            |
| brand          | json   | Null        | Brands                     |                            |
| item           | json   | Null        | Items                      |                            |
 | custom_fields  | json   | Null        | Custom Fields              |                            |
