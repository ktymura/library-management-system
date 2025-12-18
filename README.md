![CI](https://github.com/ktymura/library-management-system/actions/workflows/ci.yml/badge.svg)

# Library Management System (LMS)

Projekt realizowany w ramach zajęć z **Metodyk Tworzenia Oprogramowania**.

System zarządzania biblioteką zbudowany w architekturze **mikroserwisowej**, z wykorzystaniem **FastAPI**, **PostgreSQL**, **Dockera** oraz **CI/CD**.

## Szybki start

### Wymagania

- Docker Desktop (WSL2)
- Docker Compose v2

### Uruchomienie

```bash
docker compose up --build
```

Po uruchomieniu:

- **User Service:** [http://localhost:8001/health](http://localhost:8001/health)
- **Catalog Service:** [http://localhost:8002/health](http://localhost:8002/health)
- **pgAdmin:** [http://localhost:5050](http://localhost:5050)

Po uruchomieniu systemu migracje baz danych wykonywane są automatycznie przez Alembic.

## Funkcjonalności (aktualny stan)

### User Service

- rejestracja użytkownika (`POST /auth/register`)
- logowanie użytkownika (`POST /auth/login`)
- autoryzacja oparta o JWT
- endpoint identyfikacji użytkownika (`GET /users/me`)
- obsługa ról użytkowników:
  - `READER` (domyślna)
  - `LIBRARIAN`
  - `ADMIN`
- walidacja haseł (siła hasła, limit bcrypt)
- migracje bazy danych (Alembic)
- pełna dokumentacja API w Swagger (OpenAPI)

Swagger UI dostępny pod: <http://localhost:8001/docs>

### Catalog Service

- zarządzanie katalogiem książek i egzemplarzy,
- encje domenowe:
  - `Author`,
  - `Book`,
  - `Copy`,
- pełny CRUD książek:
  - `POST /books`,
  - `GET /books`,
  - `GET /books/{id}`,
  - `PATCH /books/{id}`,
  - `DELETE /books/{id}`,
- wyszukiwanie książek:
  - `GET /books/search?query=` (wyszukiwanie po tytule lub autorze),
- zarządzanie egzemplarzami książek:
  - `POST /books/{id}/copies`,
  - `GET /books/{id}/copies`,
- autoryzacja oparta o JWT (Bearer),
- kontrola dostępu na podstawie ról:
  - tylko `LIBRARIAN` / `ADMIN` mogą modyfikować katalog,
- walidacja danych wejściowych (ISBN, rok wydania),
- migracje bazy danych (Alembic),
- dokumentacja API w Swagger (OpenAPI).

Swagger UI dostępny pod: <http://localhost:8002/docs>

## Komponenty systemu

- **user-service**
  - obsługa użytkowników i autoryzacji (JWT, role),
  - FastAPI, SQLAlchemy, Alembic
- **catalog-service**
  - obsługa katalogu książek i egzemplarzy (Author / Book / Copy),
  - wyszukiwanie książek po tytule lub autorze,
  - autoryzacja JWT (Bearer),
  - weryfikacja ról użytkowników,
  - FastAPI, SQLAlchemy 2.0, Alembic
- **PostgreSQL**
  - jedna instancja bazy danych,
  - osobne bazy logiczne dla serwisów
- **pgAdmin**
  - panel administracyjny bazy danych

## Konfiguracja środowiska

Zmienne środowiskowe przechowywane są w pliku `.env` (niecommitowanym do repozytorium).

Przykładowy plik `.env.example` zawiera m.in.:

- dane dostępowe do bazy danych,
- sekrety JWT,
- konfigurację portów,
- dane logowania do pgAdmin.

## Autoryzacja JWT (między serwisami)

System wykorzystuje tokeny JWT do autoryzacji w architekturze mikroserwisowej.

- token generowany jest przez `user-service` podczas logowania,
- token przekazywany jest w nagłówku: `Authorization: Bearer <token>`
- `catalog-service` weryfikuje token lokalnie:
- podpis (HS256),
- czas ważności (`exp`),
- wystawcę (`iss`),
- odbiorcę (`aud`),
- rola użytkownika przekazywana jest w claimie `role`.

Dostęp do endpointów modyfikujących katalog wymaga roli:

- `LIBRARIAN` lub `ADMIN`.

## Jakość i CI/CD

Projekt wykorzystuje GitHub Actions do automatycznej kontroli jakości:

- linting kodu: `ruff`
- formatowanie: `black`
- testy automatyczne: `pytest`
- pomiar pokrycia testami: `pytest-cov` (próg ≥ 60%)
- walidacja Pull Requestów przed merge do `main`

## Dokumentacja

Pełna dokumentacja projektu znajduje się w katalogu `docs/`:

- wymagania funkcjonalne i niefunkcjonalne: `docs/requirements.md`
- architektura systemu i środowisko: `docs/architecture.md`

## Workflow Git

- praca na osobnych branchach (`feature/*`)
- integracja zmian wyłącznie przez Pull Request
- merge do `main` możliwy tylko po przejściu CI
- epiki i sprinty zgodne z metodyką Scrum
