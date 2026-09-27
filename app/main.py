from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import URLCreate  #importing our Pydantic model
from app.services.url_service import (
    create_short_url,
    get_url_by_short_code
) #importing our service functions for creation and retrieval 


app = FastAPI()  #create an instance of the FastAPI class i.e. FastAPI Application

#DEFAULT ROUTE
@app.get("/")   #Tells FastAPI: When someone sends a GET request to /, run the function immediately below.
def root():
    return {"message": "URL Shortener API"}  #Returns a Python dictionary. FastAPI converts it into a JSON HTTP response.


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
    url = get_url_by_short_code(db, short_code)

    if url is None:
        raise HTTPException(
            status_code=404,
            detail="Short URL not found"
        )

    return RedirectResponse(url=url.original_url)

