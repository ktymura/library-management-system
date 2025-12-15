from app.core.config import settings
from app.core.security import decode_token
from app.models.user import User, UserRole
from sqlalchemy.orm import Session


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
    assert payload.get("role") == UserRole.READER.value
    if settings.JWT_ISSUER:
        assert payload.get("iss") == settings.JWT_ISSUER
    if settings.JWT_AUDIENCE:
        assert payload.get("aud") == settings.JWT_AUDIENCE


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


def test_register_weak_password_422(client):
    r = client.post(
        "/auth/register", json={"email": "weak@example.com", "password": "abcdefg"}
    )  # brak wielkiej, cyfry, spec
    assert r.status_code == 422


def test_register_too_long_password_422(client):
    too_long = "A" * 73 + "!"  # >72 bajtów
    r = client.post("/auth/register", json={"email": "toolong@example.com", "password": too_long})
    assert r.status_code == 422


def test_me_returns_role_field(client):
    r = client.post("/auth/register", json={"email": "role1@example.com", "password": "Strong#123"})
    assert r.status_code == 201
    login = client.post(
        "/auth/login", json={"email": "role1@example.com", "password": "Strong#123"}
    )
    token = login.json()["access_token"]
    me = client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["role"] == "READER"  # domyślnie READER


def test_admin_ping_forbidden_for_reader(client, db_session: Session):
    # zarejestruj READER
    client.post("/auth/register", json={"email": "reader@example.com", "password": "Strong#123"})
    login = client.post(
        "/auth/login", json={"email": "reader@example.com", "password": "Strong#123"}
    )
    token = login.json()["access_token"]
    r = client.get("/users/admin/ping", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 403


def test_admin_ping_allowed_for_admin(client, db_session: Session):
    # utwórz usera i awansuj na ADMIN bezpośrednio w DB (test-internal)
    client.post("/auth/register", json={"email": "boss@example.com", "password": "Strong#123"})
    user = db_session.query(User).filter(User.email == "boss@example.com").first()
    user.role = UserRole.ADMIN
    db_session.commit()

    login = client.post("/auth/login", json={"email": "boss@example.com", "password": "Strong#123"})
    token = login.json()["access_token"]
    r = client.get("/users/admin/ping", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json() == {"ok": True}


def test_register_contract_schema(client):
    r = client.post(
        "/auth/register", json={"email": "contract@example.com", "password": "Strong#123"}
    )
    assert r.status_code == 201
    assert r.headers["content-type"].startswith("application/json")
    data = r.json()
    # dokładny zestaw kluczy:
    assert set(data.keys()) == {"id", "email", "full_name", "is_active", "role"}
    assert isinstance(data["id"], int) and isinstance(data["email"], str)


def test_register_conflict_contract(client):
    client.post("/auth/register", json={"email": "dup@example.com", "password": "Strong#123"})
    r = client.post("/auth/register", json={"email": "dup@example.com", "password": "Strong#123"})
    assert r.status_code == 409
    err = r.json()
    assert set(err.keys()) == {"detail"}  # model błędu


def test_openapi_has_bearer_security(client):
    r = client.get("/openapi.json")
    assert r.status_code == 200
    doc = r.json()
    # schemat bezpieczeństwa HTTP bearer
    sec = doc["components"]["securitySchemes"]
    assert any(v.get("type") == "http" and v.get("scheme") == "bearer" for v in sec.values())


def test_login_contract_schema(client):
    client.post("/auth/register", json={"email": "ccc@example.com", "password": "Strong#123"})
    r = client.post("/auth/login", json={"email": "ccc@example.com", "password": "Strong#123"})
    assert r.status_code == 200
    data = r.json()
    assert set(data.keys()) == {"access_token", "token_type"}
    assert data["token_type"] == "bearer"


def test_me_contract_schema(client):
    client.post("/auth/register", json={"email": "me@example.com", "password": "Strong#123"})
    tok = client.post(
        "/auth/login", json={"email": "me@example.com", "password": "Strong#123"}
    ).json()["access_token"]
    r = client.get("/users/me", headers={"Authorization": f"Bearer {tok}"})
    assert r.status_code == 200
    assert set(r.json().keys()) == {"id", "email", "full_name", "is_active", "role"}
