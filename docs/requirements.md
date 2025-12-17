# Wymagania funkcjonalne

### F-01 - Rejestracja użytkownika
System musi umożliwiać założenie konta poprzez podanie niezbędnych danych (email, hasło, imię itp.).

### F-02 - Logowanie użytkownika
System musi umożliwiać logowanie za pomocą emaila i hasła oraz generować token JWT.

### F-03 - Walidacja i autoryzacja JWT
System ma wymagać ważnego tokena JWT dla operacji wymagających uprawnień.

### F-04 - Przeglądanie katalogu książek
Użytkownik może pobrać listę książek oraz szczegóły wybranej pozycji.

### F-05 - Dodawanie nowych książek (CRUD)
Bibliotekarz lub uprawniony użytkownik może dodać nową książkę do katalogu.

### F-06 - Edycja danych książki
Bibliotekarz może edytować istniejące rekordy książek.

### F-07 - Usuwanie książek
Uprawniony użytkownik może usunąć książkę z katalogu.

### F-08 - Zarządzanie egzemplarzami (kopiami)
System umożliwia dodanie, oznaczanie dostępności i aktualizację egzemplarzy książek.

### F-09 - Wypożyczanie książek
Użytkownik może wypożyczyć egzemplarz, jeśli jest dostępny.

### F-10 - Zwrot książki
System musi umożliwić zwrot egzemplarza oraz oznaczenie go jako dostępnego.

### F-11 - Historia wypożyczeń
Użytkownik może przeglądać historię swoich wypożyczeń.

### F-12 - Panel administracyjny (API)
Admin może pobierać statystyki, listy użytkowników, blokować konta itp. (opcjonalne, późniejszy sprint).

### F-13 - Integracja między serwisami (User-Service <-> Catalog-Service)
Serwisy komunikują się poprzez REST oraz RabbitMQ (np. eventy wypożyczeń).

### F-14 - Endpointy zdrowia (/health)
Każdy serwis wystawia publiczny endpoint do monitorowania stanu.

### F-15 - Obsługa błędów API
System zwraca czytelne komunikaty błędów i kody HTTP.

### F-16 - Walidacja dostępności egzemplarza
System musi weryfikować dostępność egzemplarza książki przed utworzeniem wypożyczenia i uniemożliwić wypożyczenie egzemplarza oznaczonego jako niedostępny, zwracając odpowiedni kod HTTP oraz czytelny komunikat błędu.

# Wymagania niefunkcjonalne

### N-01 - Architektura mikroserwisowa
System składa się z co najmniej dwóch serwisów: user-service i catalog-service.

### N-02 - Wydajność
API powinno obsłużyć co najmniej 50 równoległych zapytań bez degradacji wydajności (wartość do doprecyzowania).

### N-03 - Skalowalność
Każdy serwis musi być skalowalny poziomo (konteneryzacja w Dockerze).

### N-04 - Konteneryzacja
Cały system uruchamiany poprzez docker-compose.

### N-05 - Ciągła integracja
Repozytorium musi posiadać pipeline CI (lint + testy).

### N-06 - Migracje bazy danych
Każdy serwis backendowy korzysta z Alembic do utrwalania zmian schematu.

### N-07 - Standardy kodowania
Kod musi być zgodny z formatowaniem Black i powinien przejść lintowanie Ruff.

### N-08 - Bezpieczeństwo danych
Hasła muszą być hashowane, JWT podpisane, połączenia do DB - chronione.

### N-09 - Logowanie i monitoring
Serwisy muszą generować logi oraz udostępniać healthcheck.

### N-10 - Testy automatyczne
System musi mieć pokrycie testami jednostkowymi kluczowych funkcji.

### N-11 - Dokumentacja API
Każdy serwis musi posiadać dokumentację API (Swagger).

### N-12 - Obsługa błędów i odporność
Serwisy muszą obsługiwać sytuacje wyjątkowe i zapewniać minimalne ryzyko awarii.

### N-13 - Indeksy wyszukiwania (GIN)
System musi wykorzystywać indeksy typu GIN w bazie danych (PostgreSQL) dla pól wykorzystywanych w wyszukiwaniu tekstowym (np. tytuł książki, autor), w celu zapewnienia wydajnego i skalowalnego przeszukiwania katalogu.

### N-14 - Testy integracyjne z DB
System musi posiadać testy integracyjne uruchamiane na rzeczywistej instancji bazy danych (np. PostgreSQL w Dockerze), weryfikujące poprawność działania repozytoriów, migracji Alembic oraz integracji warstwy API z bazą danych.

# Changelog

### [v0.1] – 2025-12-09
- Utworzono wstępny zestaw wymagań funkcjonalnych i niefunkcjonalnych.
- Przygotowano strukturę pliku `requirements.md`.
- Dodano wersjonowanie i changelog.

### [v0.2] - 2025-12-17
- Dodano wymagania F-16, N-13, N-14.
