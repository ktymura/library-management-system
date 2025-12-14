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


## Komponenty systemu

- **user-service** – obsługa użytkowników
- **catalog-service** – obsługa katalogu książek
- **PostgreSQL** – wspólna instancja bazy danych
- **pgAdmin** – panel administracyjny bazy danych

## Jakość i CI

- linting: `ruff`
- formatowanie: `black`
- testy: `pytest`
- automatyczna walidacja w GitHub Actions przy każdym PR

## Dokumentacja

Szczegółowa dokumentacja techniczna znajduje się w katalogu:

```
docs/
├── architecture.md
```

## Workflow Git

* praca na osobnych branchach
* Pull Request jako sposób integracji z `main`
* merge tylko po przejściu CI

