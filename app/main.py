from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from datetime import datetime
import redis

from app.database import get_db
from app.schemas import URLCreate  #importing our Pydantic model
from app.services.url_service import (
    create_short_url,
    get_url_by_short_code
) #importing our service functions for creation and retrieval 
from app.redis_client import redis_client


app = FastAPI()  #create an instance of the FastAPI class i.e. FastAPI Application

#DEFAULT ROUTE
@app.get("/")   #Tells FastAPI: When someone sends a GET request to /, run the function immediately below.
def root():
    return {"message": "URL Shortener API"}  #Returns a Python dictionary. FastAPI converts it into a JSON HTTP response.

#Acts as the API layer. It receives the HTTP request, gets the database session, 
# calls the service, and constructs the HTTP response.
@app.post("/api/v1/urls")
def create_url(request: URLCreate, 
               db: Session = Depends(get_db) #FastAPI's dependency injection
               ):  #Depends(get_db) tells FastAPI: "Before you run this function, call get_db() to get a database session and pass it in the fn as the db argument.
    new_url = create_short_url(db, str(request.original_url))  #We use str(...) because Pydantic's HttpUrl is a URL-specific type rather than an ordinary Python string.

    return {
        "id": new_url.id,
        "original_url": new_url.original_url,
        "short_code": new_url.short_code
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

