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

#### circulation-service

- odpowiedzialny za obsługę wypożyczeń i zwrotów książek,
- zarządza cyklem życia wypożyczenia egzemplarza,
- przechowuje historię wypożyczeń niezależnie od katalogu,
- realizuje logikę biznesową:
  - wypożyczenie egzemplarza,
  - zwrot egzemplarza,
- komunikuje się z `catalog-service` w celu:
  - weryfikacji dostępności egzemplarza,
  - aktualizacji statusu egzemplarza (AVAILABLE ↔ LOANED),
- udostępnia endpointy:
  - `/loans` (tworzenie wypożyczenia),
  - `/loans/{loanId}/return` (zwrot wypożyczenia),
  - `/health`,
  - `/health/db`,
- wykorzystuje FastAPI, SQLAlchemy 2.0 oraz Alembic,
- posiada własną bazę danych logiczną.

## 2.2 Autoryzacja i bezpieczeństwo

System wykorzystuje mechanizm autoryzacji oparty o tokeny JWT (JSON Web Token).

- token JWT generowany jest przez **user-service** podczas logowania użytkownika,
- token przekazywany jest w nagłówku `Authorization: Bearer <token>`,
- **catalog-service weryfikuje token lokalnie** (bez odpytywania user-service):
    - poprawność podpisu,
    - czas ważności (`exp`),
    - wystawcę (`iss`),
    - odbiorcę (`aud`),
- token zawiera claim `role`, który determinuje dostęp do endpointów,
- `circulation-service` weryfikuje token JWT lokalnie:
  - sprawdza poprawność podpisu,
  - waliduje `exp`, `iss` oraz `aud`,
  - wykorzystuje claim `role` do kontroli dostępu do operacji wypożyczeń i zwrotów.


### Role użytkowników

Każdy użytkownik posiada przypisaną rolę:

- `READER` – rola domyślna (tylko odczyt),
- `LIBRARIAN` – zarządzanie katalogiem i egzemplarzami,
- `ADMIN` – pełne uprawnienia administracyjne.

Przykłady ograniczeń:

- `POST /books` – wymaga roli `LIBRARIAN` lub `ADMIN`,
- `POST /books/{id}/copies` – wymaga roli `LIBRARIAN` lub `ADMIN`,
- `POST /loans` – wymaga roli `LIBRARIAN` lub `ADMIN`,
- endpointy `GET` dostępne są dla wszystkich ról.

## 2.3 Integracja wypożyczeń i komunikacja między serwisami

### Proces wypożyczenia
Operacja wypożyczenia jest inicjowana przez użytkownika z rolą LIBRARIAN (lub ADMIN) podczas obsługi czytelnika w bibliotece.
- POST /loans w circulation-service wymaga roli LIBRARIAN lub ADMIN.
- W żądaniu przekazywane są:
    - copy_id – identyfikator egzemplarza,
    - user_id – identyfikator czytelnika, któremu wypożyczany jest egzemplarz.
- circulation-service realizuje logikę domenową i tworzy rekord Loan (status ACTIVE).
- Następnie circulation-service aktualizuje status egzemplarza w catalog-service (np. AVAILABLE -> LOANED).

### Proces zwrotu

Zwrot inicjuje bibliotekarz (LIBRARIAN/ADMIN) przez POST /loans/{loanId}/return.
- circulation-service:
    - wyszukuje Loan,
    - waliduje, że Loan ma status ACTIVE,
    - ustawia Loan.status=RETURNED i returned_at,
    - aktualizuje status egzemplarza w catalog-service: LOANED -> AVAILABLE.

### Autoryzacja service-to-service
catalog-service chroni operacje modyfikujące status egzemplarzy przy użyciu JWT i wymaga roli LIBRARIAN lub ADMIN.

W komunikacji serwis–serwis circulation-service używa serwisowego tokenu JWT z rolą ADMIN (konfigurowanego w zmiennej środowiskowej SERVICE_JWT) do wywołań aktualizujących status kopii w catalog-service. Token jest generowany przez user-service i wykorzystywany wyłącznie do komunikacji wewnętrznej.

### Spójność danych i odporność na błędy
Aby ograniczyć niespójność między serwisami, circulation-service stosuje kompensację:
- jeśli utworzenie Loan zakończy się sukcesem, ale aktualizacja statusu kopii w catalog-service nie powiedzie się, rekord Loan jest wycofywany (usuwany) w tej samej transakcji,
- jeśli aktualizacja w catalog-service nie powiedzie się podczas zwrotu, circulation-service cofa zmianę w Loan (przywraca ACTIVE i returned_at=None) i zwraca błąd integracji.
Dodatkowo baza danych circulation-service posiada ograniczenie zapewniające, że dla jednego copy_id może istnieć tylko jedno aktywne wypożyczenie (ACTIVE) w danym momencie (partial unique index).

## 3. Baza danych

System korzysta z **jednej instancji PostgreSQL**, w której:

- tworzona jest baza i użytkownik dla `user-service`,
- tworzona jest baza i użytkownik dla `catalog-service`,
- tworzona jest baza i użytkownik dla `circulation-service`.

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
Dla `circulation-service` migrowane są m.in.:
- tabela `loans`,
- typ ENUM `loan_status` (ACTIVE, RETURNED),
- znaczniki czasu wypożyczenia i zwrotu.

## 3.3 Wydajność wyszukiwania i indeksy GIN

W celu zapewnienia wysokiej wydajności wyszukiwania książek po tytule i autorze,
`catalog-service` wykorzystuje indeksy typu **GIN (Generalized Inverted Index)** z rozszerzeniem `pg_trgm`.

### Mechanizm wyszukiwania

Wyszukiwanie realizowane jest na poziomie bazy danych PostgreSQL z użyciem operatora:

- `ILIKE '%<query>%'`

Zapytania obejmują:
- pole `books.title`,
- pole `authors.full_name` (poprzez JOIN z tabelą `authors`).

### Zastosowane indeksy

Dla przyspieszenia operacji `ILIKE` zastosowano indeksy GIN oparte o trigramy:

- `books.title` → indeks `GIN (title gin_trgm_ops)`
- `authors.full_name` → indeks `GIN (full_name gin_trgm_ops)`

Indeksy te są tworzone w dedykowanej migracji Alembic i współistnieją
z klasycznymi indeksami B-tree (np. na potrzeby sortowania lub wyszukiwania exact-match).

### Rozszerzenie pg_trgm

Baza danych `catalog-service` korzysta z rozszerzenia PostgreSQL:

- `pg_trgm`

Rozszerzenie to umożliwia efektywne porównywanie fragmentów tekstu
i jest wymagane do działania operatora `gin_trgm_ops`.


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

## 5.1 Tryb demo i seed danych

Projekt wspiera tryb **demo**, który umożliwia szybkie uruchomienie systemu z przykładowymi danymi
(użytkownicy, książki, egzemplarze, wypożyczenia) bez ręcznego klikania w API.

### Flagi środowiskowe

- `APP_ENV` – określa tryb działania aplikacji.
  - `APP_ENV=demo` lub `APP_ENV=dev` włącza możliwość seedowania danych.
- `SEED_DATA=true` – opcjonalna flaga wymuszająca seedowanie (override), użyteczna w testach lokalnych.

Seedowanie jest blokowane w innych trybach (np. produkcyjnych) w celu uniknięcia przypadkowego wstrzyknięcia danych demo.

### Uruchamianie seedowania

Seedowanie uruchamiane jest ręcznie, wewnątrz kontenerów aplikacyjnych, przez moduł `app.seed.run`:

- `user-service`:
  - `docker compose exec user-service python -m app.seed.run`
- `catalog-service`:
  - `docker compose exec catalog-service python -m app.seed.run`
- `circulation-service`:
  - `docker compose exec circulation-service python -m app.seed.run`

Dostępny jest również skrypt uruchamiający wszystkie seedy sekwencyjnie (np. `seed-all.ps1`), który:
1) seeduje użytkowników,
2) seeduje katalog (autorzy/książki/egzemplarze),
3) seeduje przykładowe wypożyczenia.

### Idempotentność

Seedowanie jest **idempotentne** – ponowne uruchomienie nie tworzy duplikatów danych.
Mechanizm opiera się o unikalne atrybuty encji, m.in.:
- `User.email`
- `Book.isbn`
- `Copy.inventory_code`

Dla wypożyczeń (`Loan`) seedowanie sprawdza istnienie rekordu przed dodaniem, aby uniknąć duplikacji
(np. ponownego tworzenia wypożyczenia dla tego samego `user_id` i `copy_id`).


## 6. Healthchecki

Każdy serwis udostępnia endpoint `/health`, który:

- zwraca HTTP 200,
- wykorzystywany jest przez Docker do monitorowania stanu kontenera.

Dodatkowo `circulation-service` udostępnia endpoint `/health/db`, który weryfikuje połączenie z bazą danych.

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
- dokumentacja OpenAPI z obsługą Bearer Auth,
- uruchomiony mikroserwis circulation-service,
- endpoint POST /loans zabezpieczony rolą LIBRARIAN/ADMIN oraz integracja z catalog-service (zmiana statusu kopii),
- niezależna baza danych dla wypożyczeń,
- migracje tabel wypożyczeń (loans),
- healthcheck aplikacji i połączenia z bazą danych.

Projekt posiada stabilny fundament architektoniczny i jest gotowy do dalszej rozbudowy funkcjonalnej.
