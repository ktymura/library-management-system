# Architektura i środowisko projektu

## 1. Cel dokumentu

Dokument opisuje architekturę techniczną projektu **Library Management System** oraz sposób konfiguracji środowiska uruchomieniowego.


## 2. Architektura systemu

Projekt zrealizowany jest w architekturze mikroserwisowej. Każdy serwis:

- działa w osobnym kontenerze Dockera,
- posiada własną bazę danych logiczną,
- komunikuje się przez REST API.

### 2.1 Serwisy

#### user-service

- odpowiedzialny za obsługę użytkowników i autoryzację,
- realizuje rejestrację, logowanie oraz identyfikację użytkownika,
- generuje i weryfikuje tokeny JWT,
- obsługuje role użytkowników (READER / LIBRARIAN / ADMIN),
- udostępnia endpointy:
  - `/auth/register`
  - `/auth/login`
  - `/users/me`
  - `/health`,
- wykorzystuje FastAPI oraz SQLAlchemy + Alembic.

#### catalog-service

- odpowiedzialny za katalog książek i egzemplarzy,
- zarządza encjami: **Author**, **Book**, **Copy**,
- realizuje pełny CRUD dla książek oraz zarządzanie egzemplarzami,
- umożliwia wyszukiwanie książek po tytule lub autorze (filtrowanie na poziomie bazy danych),
- egzekwuje autoryzację na podstawie JWT i ról użytkowników,
- weryfikuje podpis, issuer (`iss`) oraz audience (`aud`) tokenu JWT,
- udostępnia endpointy:
    - `/authors`,
    - `/books`,
    - `/books/search`,
    - `/books/{id}/copies`,
    - `/health`,
- wykorzystuje FastAPI, SQLAlchemy 2.0 oraz Alembic.

## 2.2 Autoryzacja i bezpieczeństwo

System wykorzystuje mechanizm autoryzacji oparty o tokeny JWT (JSON Web Token).

- token JWT generowany jest przez **user-service** podczas logowania użytkownika,
- token przekazywany jest w nagłówku `Authorization: Bearer <token>`,
- **catalog-service weryfikuje token lokalnie** (bez odpytywania user-service):
    - poprawność podpisu,
    - czas ważności (`exp`),
    - wystawcę (`iss`),
    - odbiorcę (`aud`),
- token zawiera claim `role`, który determinuje dostęp do endpointów.

### Role użytkowników

Każdy użytkownik posiada przypisaną rolę:

- `READER` – rola domyślna (tylko odczyt),
- `LIBRARIAN` – zarządzanie katalogiem i egzemplarzami,
- `ADMIN` – pełne uprawnienia administracyjne.

Przykłady ograniczeń:

- `POST /books` – wymaga roli `LIBRARIAN` lub `ADMIN`,
- `POST /books/{id}/copies` – wymaga roli `LIBRARIAN` lub `ADMIN`,
- endpointy `GET` dostępne są dla wszystkich ról.


## 3. Baza danych

System korzysta z **jednej instancji PostgreSQL**, w której:

- tworzona jest baza i użytkownik dla `user-service`,
- tworzona jest baza i użytkownik dla `catalog-service`.

### 3.1 Inicjalizacja bazy danych

Przy pierwszym uruchomieniu kontenera bazy danych wykonywany jest skrypt:

```
db/init/01-init.sh
```

Skrypt:

- tworzy role użytkowników bazodanowych,
- tworzy bazy danych,
- przypisuje właścicieli baz.

Skrypty inicjalizacyjne są uruchamiane **tylko przy czystym volume**.

### 3.2 Migracje bazy danych

Każdy serwis posiada własny zestaw migracji zarządzany przez Alembic.

- zmiany struktury bazy danych wersjonowane są w repozytorium,
- migracje uruchamiane są wewnątrz kontenerów aplikacyjnych,
- struktura tabel jest synchronizowana z modelami SQLAlchemy.

Dla `user-service` migrowane są m.in.:
- tabela `users`,
- role użytkowników,
- znaczniki czasu utworzenia i modyfikacji rekordów.
Dla catalog-service migrowane są m.in.:
- tabela authors,
- tabela books (ISBN, relacja do autorów, metadane publikacji),
- tabela copies (egzemplarze książek),
- typ ENUM copy_status (AVAILABLE, LOANED, LOST, DAMAGED).

## 4. Docker Compose

Plik `docker-compose.yml` definiuje:

- serwisy aplikacyjne,
- bazę danych,
- pgAdmin,
- sieć i wolumeny.

Kontenery komunikują się wewnętrznie przez nazwy serwisów (np. `db`).


## 5. Konfiguracja środowiska

Zmienne środowiskowe przechowywane są w pliku `.env` (niecommitowanym do repozytorium).

Plik `.env.example` zawiera przykładową konfigurację:

- dane dostępowe do bazy danych,
- porty serwisów,
- dane JWT (JWT_SECRET, JWT_ISSUER, JWT_AUDIENCE),
- dane logowania do pgAdmin.


## 6. Healthchecki

Każdy serwis udostępnia endpoint `/health`, który:

- zwraca HTTP 200,
- wykorzystywany jest przez Docker do monitorowania stanu kontenera.


## 7. CI/CD

Projekt wykorzystuje GitHub Actions:

- statyczną analizę kodu (Ruff),
- sprawdzanie formatowania (Black),
- uruchamianie testów automatycznych (pytest),
- weryfikację pokrycia testami (pytest-cov, próg ≥ 60%),
- walidację Pull Requestów przed merge do `main`.


## 8. Status

Zrealizowane funkcjonalności:

- system rejestracji i logowania użytkowników,
- autoryzacja oparta o JWT (HS256),
- weryfikacja `iss` i `aud` w mikroserwisach,
- obsługa ról użytkowników (READER / LIBRARIAN / ADMIN),
- katalog książek i egzemplarzy (Author / Book / Copy),
- migracje bazy danych (Alembic) w każdym serwisie,
- pełny CRUD książek oraz zarządzanie egzemplarzami,
- testy jednostkowe i integracyjne (pytest),
- automatyczne uruchamianie testów w CI,
- dokumentacja OpenAPI z obsługą Bearer Auth.

Projekt posiada stabilny fundament architektoniczny i jest gotowy do dalszej rozbudowy funkcjonalnej.
