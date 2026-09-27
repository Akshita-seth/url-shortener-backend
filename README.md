# URL Shortening & Analytics Service

A backend project built progressively to learn backend engineering concepts and system design.

## V1 — Basic URL API

### 1. Implemented:

- FastAPI application
- URL validation using Pydantic
- Short-code generation using Base62-style characters
- In-memory URL storage
- URL creation API
- Basic redirect API
- 404 handling for unknown short codes

### 2. Architecture — V1

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

### 3. Limitations:

- Data is stored only in memory.
- All URL mappings are lost when the application restarts.
- No persistent database.
- No analytics or click tracking.
- No caching.
- No idempotency or concurrency handling.
- No rate limiting.



## V2 — PostgreSQL Persistence

### 1. Implemented

- PostgreSQL database integration
- SQLAlchemy ORM
- URL database model
- Persistent URL storage
- Database sessions
- URL retrieval from PostgreSQL
- Database-level unique constraint on short codes
- PostgreSQL-backed redirects

### 2. Architecture

FastAPI
   ↓
Pydantic
   ↓
SQLAlchemy Session
   ↓
URL Service
   ↓
PostgreSQL

### 3. Limitations

- No click analytics yet.
- Every redirect queries PostgreSQL.
- No Redis caching.
- No idempotency.
- No concurrency protection for duplicate creation requests.
- No rate limiting.