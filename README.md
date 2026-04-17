# 👻 Co Robimy Wieczorem?

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.8.x-092E20.svg)](https://www.djangoproject.com/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5-7952B3.svg)]()
[![Cloudinary](https://img.shields.io/badge/Cloud-Cloudinary-blue.svg)]()

## Znasz to uczucie, gdy spędzacie dwie godziny na komunikatorze tylko po to, żeby ustalić, że... nikt nie wie, w co zagrać albo co obejrzeć? My też.

<img width="2505" height="1304" alt="image" src="https://github.com/user-attachments/assets/9fc86329-1543-4264-96ce-735c8850cdcb" />


 ### **"Co Robimy Wieczorem?"** to aplikacja webowa, która pomaga grupom znajomych błyskawicznie wybrać film, grę lub serial do wspólnego spędzenia czasu. Projekt został zrealizowany w ramach zajęć akademickich, symulując pełen cykl tworzenia aplikacji.

---

## ✨ Główne funkcjonalności

* 📅 **Wydarzenia i Premiery:** Bądź na bieżąco z nowościami! Dedykowana podstrona wykorzystująca zewnętrzne API, która automatycznie pobiera i wyświetla informacje o nadchodzących premierach ze świata rozrywki.
* 📚 **Rozbudowany Katalog:** Serce aplikacji. Wszystko w jednym miejscu: filmy, gry, seriale oraz wszelakie aktywności, podzielone na czytelne kategorie.
* 🗳️ **Pokoje głosowań:** Organizuj szybkie ankiety w prywatnych pokojach ze znajomymi. Opcje do głosowania są **bezpośrednio zintegrowane z naszym Katalogiem** – jednym kliknięciem wrzucacie do puli konkretny tytuł, film lub aktywność!
* 👤 **Zarządzanie profilami:** Zapraszaj do znajomych, zarządzaj własnym kontem i buduj swoją listę ulubionych propozycji.
* 🌍 **Rozbudowana Społeczność:** Miejsce spotkań i wymiany opinii, w którym znajdziesz:
  * 💬 **Forum dyskusyjne:** Pisz recenzje, wymieniaj opinie i dyskutuj o popkulturze.
  * 🤝 **Kluby tematyczne:** Dołączaj do dedykowanych grup (np. zrzeszających graczy lub kinomanów), w których automatycznie wyświetlają się tytuły z katalogu dopasowane do tematyki klubu.
  * ⭐ **Polecajki:** System rekomendacji pokazujący najlepsze filmy, gry i seriale, generowany dynamicznie na podstawie tego, co inni użytkownicy najczęściej dodają do swoich "Ulubionych".

---

## 🛠️ Zastosowane technologie

* **Backend:** Python 3.11+, Django 5.8.x
* **Frontend:** HTML5, CSS3, Bootstrap 5, FontAwesome, JavaScript (Vanilla)
* **Bazy danych:** SQLite3 (środowisko lokalne/deweloperskie) / PostgreSQL (Neon.tech - produkcja)
* **Zewnętrzne API:** TMDB (filmy), RAWG (gry), Jikan (anime)
* **Zarządzanie mediami:** Cloudinary API
* **Wdrażanie (Deployment):** Gunicorn, WhiteNoise (Przyszłe plany)

---

## 🚀 Instrukcja instalacji i uruchomienia 

Projekt został przygotowany tak, aby można go było łatwo uruchomić w środowisku deweloperskim. 

### 1. Wymagania systemowe
* Zainstalowany **Python w wersji 3.10 lub wyższej**.
* Zainstalowany system kontroli wersji **Git**.

### 2. Klonowanie repozytorium
Pobierz kod źródłowy na swój komputer i przejdź do katalogu projektu:

    git clone [https://github.com/OskarSrc/co-robimy-wieczorem.git](https://github.com/OskarSrc/co-robimy-wieczorem.git)
    cd webapp

### 3. Konfiguracja środowiska wirtualnego
Dla czystości należy utworzyć środowisko wirtualne:

    python -m venv .venv

    # Aktywacja w systemie Windows:
    .\.venv\Scripts\activate

    # Aktywacja w systemie macOS/Linux:
    source .venv/bin/activate

### 4. Instalacja zależności
Wszystkie niezbędne pakiety znajdują się w pliku `requirements.txt`.

    pip install -r requirements.txt

### 5. Zmienne środowiskowe (.env) i Bezpieczeństwo
Ze względów bezpieczeństwa, w repozytorium nie znajdują się klucze API, hasła do bazy danych ani klucze szyfrujące (katalogi venv, pliki cache i db.sqlite3 są ignorowane przez plik .gitignore).

Aby uruchomić projekt:
1. Utwórz w głównym katalogu (tam gdzie manage.py) plik o nazwie `.env`.
2. Uzupełnij go kluczami zgodnie z szablonem poniżej:

    `TMDB_API_KEY=`
    `RAWG_API_KEY=`
    `CLOUDINARY_CLOUD_NAME=`
    `CLOUDINARY_API_KEY=`
    `CLOUDINARY_API_SECRET=`
    `DATABASE_URL=`
      
*(Wiadomość do osoby sprawdzającej: Aktywne klucze dla tego projektu zostały przekazane w prywatnej wiadomości).*

### 6. Uruchomienie serwera

    python manage.py runserver

Aplikacja będzie dostępna pod adresem: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## 🧪 Dane testowe (Ewaluacja)

Aby ułatwić testowanie funkcjonalności bez konieczności samodzielnej rejestracji, przygotowaliśmy konto testowe bez uprawnień administracyjnych:

* **Login:** `Gosc0`
* **Hasło:** `Bardzowazne51!*`

> *Wskazówka: Jeśli chcesz wygenerować własnego administratora od zera w czystej bazie danych, użyj polecenia: python manage.py createsuperuser*

---

## 📂 Architektura i struktura projektu

Projekt opiera się na logicznym podziale na aplikacje wewnątrz frameworka Django:

    co-robimy-wieczorem/
    ├── webapp/                     # Główny katalog projektu Django
    │   ├── forum/                  # Forum dyskusyjne powiązane z wpisami z katalogu
    │   ├── katalog/                # Katalog filmów, gier, seriali i innych propozycji
    │   ├── main/                   # Strona główna, community, kluby, pokoje głosowań, wydarzenia i profile
    │   ├── media/                  # Pliki multimedialne i zasoby przesyłane przez użytkowników
    │   ├── users/                  # Dodatkowa aplikacja użytkowników, przygotowana pod dalszą rozbudowę
    │   ├── webapp/                 # Główny katalog konfiguracyjny Django (settings.py, urls.py, asgi.py, wsgi.py)
    │   ├── .env                    # Zmienne środowiskowe i klucze API
    │   ├── db.sqlite3              # Lokalna baza danych SQLite
    │   └── manage.py               # Główny skrypt zarządzający projektem Django
    ├── .gitignore                  # Reguły ignorowania plików tymczasowych i danych wrażliwych
    ├── README.md                   # Dokumentacja projektu
    └── requirements.txt            # Lista wymaganych bibliotek do instalacji

---
*Projekt zrealizowany jako wersja końcowa na zaliczenie przedmiotu, 2026 r.*

***
