import requests

URL = "http://127.0.0.1:8000/api/v1/urls"

for i in range(10):
    response = requests.post(
        URL,
        headers={
            "Idempotency-Key": f"rate-test-{i}"
        },
        json={
            "original_url": "https://example.com"
        }
    )

    print(i + 1, response.status_code)