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

- odpowiedzialny za katalog książek,
- udostępnia endpoint `/health`,
- wykorzystuje FastAPI.

## 2.2 Autoryzacja i bezpieczeństwo

System wykorzystuje mechanizm autoryzacji oparty o tokeny JWT (JSON Web Token).

- token JWT generowany jest podczas logowania użytkownika,
- token przekazywany jest w nagłówku `Authorization: Bearer <token>`,
- weryfikacja tokenu odbywa się po stronie `user-service`,
- endpointy chronione wymagają poprawnego i nieprzeterminowanego tokenu.

### Role użytkowników

Każdy użytkownik posiada przypisaną rolę:

- `READER` – rola domyślna,
- `LIBRARIAN`,
- `ADMIN`.

Dostęp do wybranych endpointów może być ograniczony na podstawie roli użytkownika.


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
- autoryzacja oparta o JWT,
- obsługa ról użytkowników,
- migracje bazy danych (Alembic),
- testy automatyczne uruchamiane w CI.

Projekt gotowy do dalszej rozbudowy funkcjonalnej.

