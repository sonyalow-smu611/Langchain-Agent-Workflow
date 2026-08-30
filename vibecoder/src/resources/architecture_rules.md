# Architecture Rules

## Frontend

Frontend code belongs under:

src/

## Backend

Backend code belongs under:

server/

## Database

Database definitions belong under:

prisma/

## Tests

Tests belong under:

tests/

## Ownership

Frontend workers must not modify backend implementation.

Backend workers must not modify frontend implementation.

Database schema changes must go through the approved schema specification.

API changes must go through the approved API contract.