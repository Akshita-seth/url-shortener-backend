import requests
import uuid
import pytest
from concurrent.futures import ThreadPoolExecutor

from app.database import SessionLocal
from app.models import URL
from app.redis_client import redis_client


BASE_URL = "http://127.0.0.1:8000"


# @pytest.fixture tells pytest: "This is setup code for tests."
# autouse=True means:"Run this automatically for every test."
# @pytest.fixture(autouse=True) means: "Run this automatically for every test." 
@pytest.fixture(autouse=True) 
def reset_rate_limit():
    redis_client.delete("rate_limit:127.0.0.1")
#we're deleting only the state causing the interference.
# We're not doing FLUSHDB because that would also delete URL-cache entries.


def unique_key():
    return f"test-{uuid.uuid4()}"


def test_create_url():
    response = requests.post(
        f"{BASE_URL}/api/v1/urls",
        headers={
            "Idempotency-Key": unique_key()
        },
        json={
            "original_url": "https://example.com"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "id" in data
    assert "short_code" in data
    assert data["original_url"] == "https://example.com/"


def test_invalid_url():
    response = requests.post(
        f"{BASE_URL}/api/v1/urls",
        headers={
            "Idempotency-Key": unique_key()
        },
        json={
            "original_url": "not-a-url"
        }
    )

    assert response.status_code == 422


def test_idempotency():
    key = unique_key()

    first_response = requests.post(
        f"{BASE_URL}/api/v1/urls",
        headers={"Idempotency-Key": key},
        json={
            "original_url": "https://example.com"
        }
    )

    second_response = requests.post(
        f"{BASE_URL}/api/v1/urls",
        headers={"Idempotency-Key": key},
        json={
            "original_url": "https://example.com"
        }
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 200

    assert (
        first_response.json()["short_code"]
        == second_response.json()["short_code"]
    )


def test_redirect():
    create_response = requests.post(
        f"{BASE_URL}/api/v1/urls",
        headers={"Idempotency-Key": unique_key()},
        json={"original_url": "https://example.com"}
    )

    assert create_response.status_code == 200

    short_code = create_response.json()["short_code"]

    redirect_response = requests.get(
        f"{BASE_URL}/{short_code}",
        allow_redirects=False
    )

    assert redirect_response.status_code == 307
    assert redirect_response.headers["location"] == "https://example.com/"



def test_nonexistent_short_code():
    response = requests.get(
        f"{BASE_URL}/does-not-exist",
        allow_redirects=False
    )

    assert response.status_code == 404


def test_analytics():
    create_response = requests.post(
        f"{BASE_URL}/api/v1/urls",
        headers={"Idempotency-Key": unique_key()},
        json={"original_url": "https://example.com"}
    )

    assert create_response.status_code == 200

    short_code = create_response.json()["short_code"]

    first_redirect = requests.get(
        f"{BASE_URL}/{short_code}",
        allow_redirects=False
    )

    second_redirect = requests.get(
        f"{BASE_URL}/{short_code}",
        allow_redirects=False
    )

    assert first_redirect.status_code == 307
    assert second_redirect.status_code == 307

    db = SessionLocal()

    try:
        url = (
            db.query(URL)
            .filter(URL.short_code == short_code)
            .first()
        )

        assert url is not None
        assert url.click_count == 2
        assert url.last_accessed_at is not None

    finally:
        db.close()


def test_idempotency_conflict():
    key = unique_key()

    first_response = requests.post(
        f"{BASE_URL}/api/v1/urls",
        headers={"Idempotency-Key": key},
        json={
            "original_url": "https://example.com"
        }
    )

    assert first_response.status_code == 200

    second_response = requests.post(
        f"{BASE_URL}/api/v1/urls",
        headers={"Idempotency-Key": key},
        json={
            "original_url": "https://google.com"
        }
    )

    assert second_response.status_code == 409


def test_concurrent_idempotency():
    key = unique_key()

    def send_request():
        response = requests.post(
            f"{BASE_URL}/api/v1/urls",
            headers={"Idempotency-Key": key},
            json={"original_url": "https://example.com"}
        )

        return response.status_code, response.json()

    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(
            executor.map(
                lambda _: send_request(),
                range(10)
            )
        )

    status_codes = [status for status, _ in results]
    responses = [data for _, data in results]

    assert all(status == 200 for status in status_codes)

    short_codes = {
        data["short_code"]
        for data in responses
    }

    assert len(short_codes) == 1


def test_rate_limit():
    responses = []

    for _ in range(6):
        response = requests.post(
            f"{BASE_URL}/api/v1/urls",
            headers={"Idempotency-Key": unique_key()},
            json={"original_url": "https://example.com"}
        )
        responses.append(response.status_code)

    assert responses[:5] == [200, 200, 200, 200, 200]
    assert responses[5] == 429


def test_cache_population():
    create_response = requests.post(
        f"{BASE_URL}/api/v1/urls",
        headers={"Idempotency-Key": unique_key()},
        json={"original_url": "https://example.com"}
    )

    assert create_response.status_code == 200

    short_code = create_response.json()["short_code"]

    # Make sure the cache is empty first
    redis_client.delete(short_code)

    # First redirect = cache miss → PostgreSQL → Redis
    response = requests.get(
        f"{BASE_URL}/{short_code}",
        allow_redirects=False
    )

    assert response.status_code == 307
    assert response.headers["location"] == "https://example.com/"

    # Redis should now contain the URL
    cached_url = redis_client.get(short_code)

    assert cached_url == "https://example.com/"