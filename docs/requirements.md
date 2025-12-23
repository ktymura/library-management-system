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

### F-17 - Rezerwacja książki
System musi umożliwiać użytkownikowi utworzenie rezerwacji wybranej książki/egzemplarza, jeśli spełnione są warunki rezerwacji.

### F-18 - Kolejka rezerwacji (FIFO)
System musi utrzymywać kolejkę rezerwacji dla danej książki w kolejności FIFO, tak aby użytkownicy byli obsługiwani zgodnie z czasem złożenia rezerwacji.

### F-19 - Okno odbioru rezerwacji
System musi definiować i egzekwować okno czasowe na odbiór rezerwacji, po którego upływie rezerwacja wygasa i kolejka przechodzi do następnej osoby.

### F-20 - Statusy rezerwacji
System musi obsługiwać statusy rezerwacji (np. ACTIVE/WAITING, READY_FOR_PICKUP, PICKED_UP, EXPIRED, CANCELLED) oraz umożliwiać ich aktualizację zgodnie z regułami biznesowymi.

### F-21 - Naliczanie kar za przetrzymanie
System musi naliczać kary za przetrzymanie wypożyczonych egzemplarzy po przekroczeniu terminu zwrotu, zgodnie z aktualną strategią naliczania.

### F-22 - Zmiana strategii kar przez admina
System musi umożliwiać administratorowi zmianę strategii naliczania kar bez konieczności modyfikacji kodu aplikacji, przy zachowaniu kontroli uprawnień.

### F-23 - Zdarzenia domenowe (Observer Pattern)
System musi generować zdarzenia domenowe dla kluczowych akcji (np. utworzenie rezerwacji, udostępnienie do odbioru, wypożyczenie, zwrot, naliczenie kary) zgodnie z podejściem Observer.

### F-24 - Reakcje systemu na zdarzenia
System musi reagować na zdarzenia domenowe poprzez uruchamianie odpowiednich procesów w sposób spójny i odporny na błędy.

### F-25 - Odbiór powiadomień (REST)
System musi udostępniać endpoint REST do odbioru powiadomień/zdarzeń z innych serwisów (np. webhook), umożliwiający przyjęcie komunikatu i jego walidację.

### F-26 - Logowanie przyjętych powiadomień
System musi rejestrować w logach oraz (opcjonalnie) w bazie danych metadane przyjętych powiadomień, aby umożliwić diagnostykę i audyt.

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
System musi wykorzystywać indeksy typu GIN w bazie danych (PostgreSQL) dla pól wykorzystywanych w wyszukiwaniu tekstowym, w celu zapewnienia wydajnego i skalowalnego przeszukiwania katalogu.

### N-14 - Testy integracyjne z DB
System musi posiadać testy integracyjne uruchamiane na rzeczywistej instancji bazy danych, weryfikujące poprawność działania repozytoriów, migracji Alembic oraz integracji warstwy API z bazą danych.

### N-15 - System komunikatów (RabbitMQ)
System musi wykorzystywać broker komunikatów do wymiany zdarzeń pomiędzy serwisami, zapewniając asynchroniczną komunikację i rozdzielenie odpowiedzialności między modułami.

### N-16 - Idempotencja i deduplikacja zdarzeń
System musi zapewniać idempotentne przetwarzanie zdarzeń (wielokrotne dostarczenie tego samego komunikatu nie może powodować podwójnych skutków), w tym mechanizm deduplikacji.

### N-17 - Audyt i śledzenie zdarzeń
System musi umożliwiać śledzenie przepływu zdarzeń end-to-end, a także przechowywać historię przetwarzania w celu analizy i rozliczalności.

### N-18 - Konfigurowalność strategii
System powinien umożliwiać konfigurację strategii biznesowych poprzez ustawienia środowiskowe lub konfigurację serwisową, bez potrzeby przebudowy aplikacji.

### N-19 - Dokumentacja wzorców projektowych
System musi posiadać dokumentację opisującą zastosowane wzorce projektowe.

# Changelog

### [v0.1] – 2025-12-09
- Utworzono wstępny zestaw wymagań funkcjonalnych i niefunkcjonalnych.
- Przygotowano strukturę pliku `requirements.md`.
- Dodano wersjonowanie i changelog.

### [v0.2] - 2025-12-17
- Dodano wymagania F-16, N-13, N-14.

### [v0.3] - 2025-12-23
- Dodano wymagania F-17 do F-26 oraz N-15 do N-19.
