import redis
import os
from fastapi import Request, HTTPException
#Request : gives us information about the incoming HTTP request.

from app.redis_client import redis_client


# RATE_LIMIT = 5
# WINDOW_SECONDS = 60

RATE_LIMIT = int(os.getenv("RATE_LIMIT", "5"))
WINDOW_SECONDS = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))


def check_rate_limit(request: Request):  #receives the incoming FastAPI Request
    client_ip = request.client.host  #gives us the client's IP address.

    # Create the Redis key
    key = f"rate_limit:{client_ip}" #This is a Python f-string
    # key beconmes something like "rate_limit:<client_ip>" -> ex: rate_limit:127.0.0.1
    


    #Everything involving Redis goes inside the try block.
    # Why? Because Redis could be unavailable.
    try:
        request_count = redis_client.incr(key)
        # ex: intially, rate_limit:127.0.0.1 = 4, after increment -> rate_limit:127.0.0.1 = 5

        #Is this the first request in the current window?
        if request_count == 1:  
            redis_client.expire(key, WINDOW_SECONDS)  # Set TTL for the key of WINDOW_SIZE
        #Make Redis automatically delete this key after 60 seconds.
    
        if request_count > RATE_LIMIT:
            raise HTTPException(
                status_code=429,
                detail="Too many requests. Please try again later."
            )

    except redis.RedisError:  #lets us catch Redis-related failures.
        # Redis failure should not make the API unavailable.
        pass
    #So if Redis is unavailable, the request is allowed through instead of the entire API failing.
    #This is called graceful degradation.