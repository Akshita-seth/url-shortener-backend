from fastapi import Depends, FastAPI, HTTPException, Header
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import datetime
import redis
import hashlib
from sqlalchemy.exc import IntegrityError


from app.database import get_db
from app.schemas import URLCreate  #importing our Pydantic model
from app.services.url_service import (
    create_short_url,
    get_url_by_short_code
) #importing our service functions for creation and retrieval 
from app.redis_client import redis_client
from app.models import IdempotencyKey


app = FastAPI()  #create an instance of the FastAPI class i.e. FastAPI Application

#DEFAULT ROUTE
@app.get("/")   #Tells FastAPI: When someone sends a GET request to /, run the function immediately below.
def root():
    return {"message": "URL Shortener API"}  #Returns a Python dictionary. FastAPI converts it into a JSON HTTP response.



#Acts as the API layer. It receives the HTTP request, gets the database session, 
# calls the service, and constructs the HTTP response.
@app.post("/api/v1/urls")
def create_url(request: URLCreate, 
               db: Session = Depends(get_db), #FastAPI's dependency injection => #Depends(get_db) tells FastAPI: "Before you run this function, call get_db() to get a database session and pass it in the fn as the db argument.
               idempotency_key: str = Header(..., alias="Idempotency-Key")  #FastAPI, take the Idempotency-Key HTTP header and give its value to the variable idempotency_key (... means this header is required, and alias="Idempotency-Key" tells FastAPI to look for the HTTP header with that exact name, including the hyphen)
        ):    #Header(...) This tells FastAPI: Don't get this value from the JSON body or URL path. Get it from an HTTP request header.
              #The alias tells FastAPI:The HTTP header is actually called Idempotency-Key; put its value into the Python variable idempotency_key.


    #calculate a request hash
    request_hash = hashlib.sha256(
        str(request.original_url).encode()
    ).hexdigest() 

    #check whether we've seen this key before
    existing_key = (
        db.query(IdempotencyKey)
        .filter(IdempotencyKey.key == idempotency_key)
        .first()
    )

    if existing_key is not None:

        # Checks if the key is being reused for a different request i.e. matches the original_url input via their hash
        if existing_key.request_hash != request_hash:
            raise HTTPException(
                status_code=409,
                detail="Idempotency-Key was already used for a different request"
            )

        #No new short code is generated.
        existing_url = get_url_by_short_code(
            db,
            existing_key.short_code
        )
        # redirects the existing short code to the original URL
        return {
            "id": existing_url.id,
            "original_url": existing_url.original_url,
            "short_code": existing_url.short_code
        }
    
    #time.sleep(0.5)  # Simulate a delay to test race conditions in V6
    
    try:
         # Creates URL and flushes it, but does NOT commit yet
        new_url = create_short_url(
                 db,
                 str(request.original_url)
       )

        # Create idempotency record
        new_idempotency_key = IdempotencyKey(
              key=idempotency_key,
              short_code=new_url.short_code,
              request_hash=request_hash
        )

        db.add(new_idempotency_key)

        db.commit()   # Commit URL + idempotency record together

        return {
             "id": new_url.id,
             "original_url": new_url.original_url,
             "short_code": new_url.short_code
        }

    except IntegrityError:
           # Undo the failed transaction 
           db.rollback()

            # Another concurrent request probably created the key first. Retrieve the existing record and return it.
           existing_key = (
               db.query(IdempotencyKey)
               .filter(IdempotencyKey.key == idempotency_key)
               .first()
           )

    if existing_key is None:
        raise

    # Return the URL created by the winning request 
    existing_url = get_url_by_short_code(
        db,
        existing_key.short_code
    )

    return {
        "id": existing_url.id,
        "original_url": existing_url.original_url,
        "short_code": existing_url.short_code
    }


@app.get("/{short_code}")
def redirect_to_url(
    short_code: str,
    db: Session = Depends(get_db)
):
    try: #for handling redis failure if unavailble, gracefully 
        original_url = redis_client.get(short_code)
    except redis.RedisError:
        original_url = None

    if original_url is None:  #redis cache miss
        url = get_url_by_short_code(db, short_code)  #seacrches in db

        if url is None:
            raise HTTPException(
                status_code=404,
                detail="Short URL not found"
            )

        original_url = url.original_url

        #store in redis so the next request can use redis, but only possible if redis avaailable therefore andling redis failure gracefully
        try:
            redis_client.set(
                short_code,
                original_url,
                ex=3600
            )
        except redis.RedisError:
            pass

    else:
        url = get_url_by_short_code(db, short_code)

    # Update click count and last accessed timestamp
    url.click_count += 1
    url.last_accessed_at = datetime.now()
    #only modify the SQLAlchemy Python object initially

    db.commit()  #persists those changes to PostgreSQL
    return RedirectResponse(url=url.original_url)

