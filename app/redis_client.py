import redis

#Creates a Redis client object
redis_client = redis.Redis( 
    host="localhost", #Redis is running on our own computer through Docker
    port=6379,  #Connect to Redis through its port
    decode_responses=True  #tells the Redis client to return values as normal Python strings ("https://google.com") instead of byte strings(b"https://google.com")
)
#Creating this object does not yet mean we've performed a Redis lookup. We're just configuring a client that knows where Redis is
