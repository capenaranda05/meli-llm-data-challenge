# rule_custom_field Table

The `rule_custom_field` table stores , receiving data from PME.

The table has the following columns:

| Field       | Type           | Constraints | Description                | Extra                   |
|-------------|----------------|-------------|----------------------------|-------------------------|
| id          | bigint         | Not null    | Auto-increment primary key |                         |
| rule_row_id | bigint         | Not null    | Foreign                    | REFERENCES rule_row(id) |
| name        | varchar(180)   | Not null    | Name                       |                         |
| value_info  | varchar(180)   | Not null    | Values                     |                         |
| 
