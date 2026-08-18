# Database Guidelines

- Every model should have a primary key.
- Relationships should be explicit.
- Avoid unnecessary duplication.
- Add indexes when justified by query patterns.
- Schema changes should be represented as migrations.
- Do not change the database schema without updating SchemaSpec.