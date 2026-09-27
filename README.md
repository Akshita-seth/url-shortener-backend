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

## V3 — Redirect Analytics

### 1. Implemented

- Click count tracking
- Last accessed timestamp
- PostgreSQL-backed analytics updates
- Persistent analytics data on every successful redirect

### 2. Architecture

Client
   ↓
FastAPI
   ↓
SQLAlchemy Session
   ↓
PostgreSQL
   ↓
Find URL + Update Analytics
   ↓
HTTP Redirect

### 3. Limitations:
- Every redirect queries PostgreSQL.
- High redirect traffic can increase database load.
- No caching yet.
- No Redis integration.
- No idempotency or rate limiting.


## V4 — Redis Caching

### 1. Implemented

- Redis integration for URL caching
- Cache-aside pattern for short-code lookups
- Redis cache HIT and MISS handling
- PostgreSQL fallback on cache MISS
- 1-hour TTL for cached URLs
- Graceful fallback when Redis is unavailable
- PostgreSQL remains the source of truth
- Analytics continue to be stored in PostgreSQL

### 2. Architecture

Client
   ↓
FastAPI
   ↓
Redis
 ┌─┴───────────┐
HIT           MISS
 ↓              ↓
URL         PostgreSQL
 ↓              ↓
Analytics   Redis SET
 └──────┬───────┘
        ↓
     Redirect


### 3. Limitations

- Analytics still require a PostgreSQL operation on every redirect.
- Cache invalidation is not implemented because URL updates are not currently supported.
- Redis failure can add latency because the application first attempts the Redis connection before falling back to PostgreSQL.
- No rate limiting yet.
- No idempotency or concurrent-request protection yet.