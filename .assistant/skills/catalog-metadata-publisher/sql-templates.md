# Publication SQL templates

Always quote identifiers with backticks and SQL string values with escaped single quotes.

## Comments

```sql
COMMENT ON TABLE `<catalog>`.`<schema>`.`<table>` IS '<comment>';

COMMENT ON COLUMN `<catalog>`.`<schema>`.`<table>`.`<column>` IS '<comment>';
```

Use `IS NULL` only in explicitly approved rollback statements.

## Tags

```sql
ALTER TABLE `<catalog>`.`<schema>`.`<table>`
SET TAGS ('<tag>' = '<value>');

ALTER TABLE `<catalog>`.`<schema>`.`<table>`
ALTER COLUMN `<column>`
SET TAGS ('<tag>' = '<value>');
```

Apply column tags one column at a time. Respect governed-tag permissions and platform limits.

## Informational keys

```sql
ALTER TABLE `<catalog>`.`<schema>`.`<parent>`
ADD CONSTRAINT `<constraint_name>`
PRIMARY KEY (`<pk_column>`) NOT ENFORCED;

ALTER TABLE `<catalog>`.`<schema>`.`<child>`
ADD CONSTRAINT `<constraint_name>`
FOREIGN KEY (`<fk_column>`)
REFERENCES `<catalog>`.`<schema>`.`<parent>` (`<pk_column>`)
NOT ENFORCED;
```

For composite keys, preserve the declared order on both sides. Add `RELY` only when the integrity and cardinality validations required by policy have completed successfully.

Before emitting key DDL, verify the table is an eligible Delta table and query existing constraint names to avoid collisions.
