# API Conventions

APIs should use REST-style HTTP methods.

GET:
Retrieve resources.

POST:
Create resources.

PUT/PATCH:
Update resources.

DELETE:
Remove resources.

Successful responses should return structured JSON.

Errors should follow:

{
    "error": "Human-readable message",
    "code": "MACHINE_READABLE_CODE"
}