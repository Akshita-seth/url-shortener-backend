#Contains the actual URL creation logic.

import secrets  #gives us functions for generating unpredictable random values
import string   #provides useful predefined character sets

from sqlalchemy.orm import Session

from app.models import URL

# The function accepts an integer called length, and if we don't provide one, use 6.
def generate_short_code(length: int = 6) -> str:  # Type Hint -> like sugar jars i.e. expceted to return a string but python won't force it
    characters = string.ascii_letters + string.digits  
     #gives a-z, A-Z, 0-9. 62 possible characters. 62^6 = 56 billion possible combinations. This is enough for our use case. 
     #This is why we call this a Base62-style short code

    return "".join(   # joins the selected characters
        secrets.choice(characters)  #secrets.choice(characters)
        for _ in range(length)    #runs that selection length(dafault 6) times
    )

#This function receives the original URL and returns a URL model object
#Session and URL in the annotation are type hints.
def create_short_url(db: Session, original_url: str) -> URL:
    short_code = generate_short_code()

    new_url = URL(
        original_url=original_url,
        short_code=short_code
    ) #creates a SQLAlchemy object.

    db.add(new_url) # push
    db.flush() # sync with database without committing

    return new_url #URL model object

def get_url_by_short_code(db: Session, short_code: str) -> URL | None:
    return (
        db.query(URL)
        .filter(URL.short_code == short_code)
        .first() # returns the first matching row URL or None Because short_code is UNIQUE, at most one matching row  
    ) #function returns either a URL object or None