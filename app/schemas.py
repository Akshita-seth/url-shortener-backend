from pydantic import BaseModel, HttpUrl
# BaseModel → lets us define a structured request model.
# HttpUrl → validates that the value is a valid HTTP/HTTPS URL.

class URLCreate(BaseModel): #creates our own model called URLCreate
    original_url: HttpUrl  #The request must contain a field called original_url, and it must be a valid URL