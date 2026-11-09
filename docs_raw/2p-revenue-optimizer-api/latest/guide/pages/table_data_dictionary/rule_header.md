# rule_header Table

The `rule_header` table stores , receiving data from PME.

The table has the following columns:

| Field                    | Type         | Constraints | Description                     | Extra                    |
|--------------------------|--------------|-------------|---------------------------------|--------------------------|
| id                       | bigint       | Not null    | Auto-increment primary key      |                          |
| type                     | varchar(180) | Not null    |                                 |                          |
| date                     | timestamp    | Not null    | Date timestamp when was created | DEFAULT_GENERATED        |
| username                 | varchar(180) | Not null    | Username who created rule       |                          |
| name                     | varchar(180) | Not null    | Name of rule                    |                          |
| description              | varchar(180) | Not null    | Description                     |                          |
| productive               | boolean      | Not null    | Is productive                   |                          |
| version                  | int          | Not null    | Version                         |                          |
| 
