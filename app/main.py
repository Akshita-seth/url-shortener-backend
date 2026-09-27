from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse

from app.schemas import URLCreate  #importing our Pydantic model
from app.services.url_service import create_short_url,urls  #importing our service function and the temporary database


app = FastAPI()  #create an instance of the FastAPI class i.e. FastAPI Application


@app.get("/")   #Tells FastAPI: When someone sends a GET request to /, run the function immediately below.
def root():
    return {"message": "URL Shortener API"}  #Returns a Python dictionary. FastAPI converts it into a JSON HTTP response.


@app.post("/api/v1/urls")
def create_url(request: URLCreate):
    short_code = create_short_url(str(request.original_url))  #We use str(...) because Pydantic's HttpUrl is a URL-specific type rather than an ordinary Python string.

    return {
        "original_url": str(request.original_url),
        "short_code": short_code
    }


@app.get("/{short_code}")
def redirect_to_url(short_code: str):
    if short_code not in urls:
        raise HTTPException(status_code=404, detail="Short URL not found")

    original_url = urls[short_code]

    return RedirectResponse(url=original_url) #Return an HTTP redirect response pointing to this URL