from app.core.security import decode_token


def test_register_success(client):
    r = client.post(
        "/auth/register", json={"email": "alice@example.com", "password": "S3curePass!"}
    )
    assert r.status_code == 201
    data = r.json()
    assert data["email"] == "alice@example.com"
    assert "id" in data
    assert data["is_active"] is True


def test_register_duplicate_email(client):
    client.post("/auth/register", json={"email": "bob@example.com", "password": "Secret123!"})
    r2 = client.post("/auth/register", json={"email": "bob@example.com", "password": "Another123!"})
    assert r2.status_code in (409, 400)  # preferujemy 409


def test_login_success_and_token(client):
    client.post("/auth/register", json={"email": "carol@example.com", "password": "Strong#123"})
    r = client.post("/auth/login", json={"email": "carol@example.com", "password": "Strong#123"})
    assert r.status_code == 200
    tok = r.json()["access_token"]
    assert isinstance(tok, str) and len(tok) > 10
    # token powinien się dać zdekodować
    payload = decode_token(tok)
    assert "sub" in payload


def test_login_invalid_credentials(client):
    client.post("/auth/register", json={"email": "dave@example.com", "password": "Qwerty!123"})
    r = client.post("/auth/login", json={"email": "dave@example.com", "password": "badpass"})
    assert r.status_code == 401


def test_me_requires_auth(client):
    r = client.get("/users/me")
    assert r.status_code == 401


def test_me_with_token(client):
    client.post("/auth/register", json={"email": "eve@example.com", "password": "Abcdef!234"})
    login = client.post("/auth/login", json={"email": "eve@example.com", "password": "Abcdef!234"})
    token = login.json()["access_token"]
    r = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    data = r.json()
    assert data["email"] == "eve@example.com"
    assert data["is_active"] is True
