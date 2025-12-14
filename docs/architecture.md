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

- odpowiedzialny za obsługę użytkowników,
- udostępnia endpoint `/health` do sprawdzania stanu serwisu,
- wykorzystuje FastAPI.

#### catalog-service

- odpowiedzialny za katalog książek,
- udostępnia endpoint `/health`,
- wykorzystuje FastAPI.


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

- linting kodu,
- uruchamianie testów,
- walidacja PR przed merge do `main`.


## 8. Status

Aktualny stan projektu:

- środowisko Docker skonfigurowane,
- serwisy działają poprawnie,
- baza danych inicjalizowana automatycznie.

Projekt gotowy do dalszej rozbudowy funkcjonalnej.
