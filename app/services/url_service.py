import secrets  #gives us functions for generating unpredictable random values
import string   #provides useful predefined character sets


urls = {}   # creates an empty Python dictionary {short code → original URL}. Temporary Database

# The function accepts an integer called length, and if we don't provide one, use 6.
def generate_short_code(length: int = 6) -> str:  # Type Hint -> like sugar jars i.e. expceted to return a string but python won't force it
    characters = string.ascii_letters + string.digits  
     #gives a-z, A-Z, 0-9. 62 possible characters. 62^6 = 56 billion possible combinations. This is enough for our use case. 
     #This is why we call this a Base62-style short code

    return "".join(   # joins the selected characters
        secrets.choice(characters)  #secrets.choice(characters)
        for _ in range(length)    #runs that selection length(dafault 6) times
    )

#This function receives the original URL.
def create_short_url(original_url: str) -> str:
    short_code = generate_short_code()

    urls[short_code] = original_url

    return short_code