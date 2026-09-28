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


## V5 — Idempotent URL Creation

### 1. Implemented

- Idempotency-Key support for URL creation requests
- PostgreSQL-backed idempotency records
- SHA-256 request fingerprinting
- Detection of repeated requests using the same Idempotency-Key
- Repeated identical requests return the same short code
- Reuse of an Idempotency-Key with different request data returns `409 Conflict`
- Unique database constraint on Idempotency-Key

### 2. Architecture


Client
   ↓
POST /api/v1/urls
   ↓
Idempotency-Key
   ↓
Request Hash
   ↓
PostgreSQL
   ↓
Check Idempotency-Key
   ├── New Key
   │     ↓
   │   Create URL
   │     ↓
   │   Store Key + Short Code + Hash
   │
   └── Existing Key
         ↓
      Compare Hash
       ├── Same → Return Existing Short Code
       └── Different → 409 Conflict


### 3. Limitations

- Sequential duplicate requests are handled correctly.
- Concurrent requests using the same Idempotency-Key can still encounter a race condition.
- Application-level existence checks are not sufficient by themselves to guarantee concurrency safety.
- Concurrent idempotency handling will be addressed in V6.
- No rate limiting yet.

## V6 — Concurrent Idempotency Protection

### 1. Implemented

- Concurrent request testing with 10 simultaneous requests
- Database-level protection using a unique constraint on `Idempotency-Key`
- Proper transaction handling for URL and idempotency record creation
- SQLAlchemy `flush()` used to stage the URL without committing
- URL and idempotency record committed as a single transaction
- `IntegrityError` handling for concurrent duplicate requests
- Transaction rollback when a concurrent insert conflict occurs
- Retrieval of the already-created URL after a concurrency conflict
- All concurrent requests return the same URL instead of creating duplicates or returning errors

### 2. Architecture


10 Concurrent Requests
          ↓
   Idempotency-Key
          ↓
   Check Existing Key
          ↓
   ┌──────┴───────┐
   ↓              ↓
New Key      Existing Key
   ↓              ↓
Create URL    Return Existing URL
   ↓
Flush
   ↓
Create Idempotency Record
   ↓
Commit Transaction
   ↓
   ┌──────────────┐
   │              │
Success       Conflict
   │              │
   ↓              ↓
Commit       Rollback
                  ↓
          Retrieve Existing URL
                  ↓
             Return Same URL


### Limitations:

- Rate limiting is not implemented yet.
- The current rate-limiting protection will be added using Redis in V7.
- Analytics are still persisted in PostgreSQL on every redirect.