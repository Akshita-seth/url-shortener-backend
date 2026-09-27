# URL Shortening & Analytics Service

A backend project built progressively to learn backend engineering concepts and system design.

### V1 — Basic URL API

#### Implemented:

- FastAPI application
- URL validation using Pydantic
- Short-code generation using Base62-style characters
- In-memory URL storage
- URL creation API
- Basic redirect API
- 404 handling for unknown short codes

#### Architecture — V1

```text
Client
   ↓
FastAPI
   ↓
Pydantic Validation
   ↓
URL Service
   ↓
Python Dictionary
   ↓
Redirect

#### Limitations:
- Data is stored only in memory.
- All URL mappings are lost when the application restarts.
- No persistent database.
- No analytics or click tracking.
- No caching.
- No idempotency or concurrency handling.
- No rate limiting.
