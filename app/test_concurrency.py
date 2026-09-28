import requests
from concurrent.futures import ThreadPoolExecutor


URL = "http://127.0.0.1:8000/api/v1/urls"


def send_request():
    response = requests.post(
        URL,
        headers={
            "Idempotency-Key": "final-test"
        },
        json={
            "original_url": "https://example.com"
        }
    )

    return response.status_code, response.text


#We're creating a pool capable of running 10 requests concurrently.
with ThreadPoolExecutor(max_workers=10) as executor:
    results = list(
        executor.map(
            lambda _: send_request(),
            range(10)
        )
    )


for result in results:
    print(result)