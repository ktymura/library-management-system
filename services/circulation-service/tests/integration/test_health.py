import os


def test_health_db_endpoint(client):
    print(os.getenv("DATABASE_URL"))
    resp = client.get("/health/db")
    assert resp.status_code == 200
