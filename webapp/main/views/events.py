import os
from datetime import date, timedelta

import requests
from django.shortcuts import render


tmdb_key = os.getenv("TMDB_API_KEY")
rawg_key = os.getenv("RAWG_API_KEY")


def widok_eventow(request):
    dzisiaj = date.today()
    za_pol_roku = dzisiaj + timedelta(180)

    filmy = []
    try:
        url_filmy = f"https://api.themoviedb.org/3/movie/upcoming?api_key={tmdb_key}&language=pl-PL&page=1"
        odp = requests.get(url_filmy, timeout=5)

        if odp.status_code == 200:
            dane = odp.json()
            surowa_lista_filmy = dane.get("results", [])[:15]
            surowa_lista_filmy = [
                m
                for m in surowa_lista_filmy
                if m.get("release_date") and m.get("release_date") >= str(dzisiaj)
            ]
            filmy = sorted(surowa_lista_filmy, key=lambda film: film.get("release_date", ""))[:20]
        else:
            print("Nie wykryto klucza API.")

    except Exception as error:
        print(f"Błąd pobierania: {error}")

    gry = []
    if rawg_key:
        try:
            url_gry = f"https://api.rawg.io/api/games?key={rawg_key}&dates={dzisiaj},{za_pol_roku}&ordering=released"
            odp_gry = requests.get(url_gry, timeout=5)
            if odp_gry.status_code == 200:
                dane_gry = odp_gry.json()
                gry = dane_gry.get("results", [])[:15]

        except Exception as error:
            print(f"Błąd pobierania gier: {error}")

    else:
        print("Nie wykryto klucza API.")

    anime = []
    try:
        url_anime = "https://api.jikan.moe/v4/seasons/upcoming"
        odp_anime = requests.get(url_anime, timeout=5)

        if odp_anime.status_code == 200:
            dane_anime = odp_anime.json()
            surowa_lista_anime = dane_anime.get("data", [])[:15]

            surowa_lista_anime = [
                a
                for a in surowa_lista_anime
                if a.get("aired") and a["aired"].get("from") and a["aired"]["from"] >= str(dzisiaj)
            ]
            anime = sorted(surowa_lista_anime, key=lambda a: a["aired"]["from"])[:20]
        else:
            print("Nie wykryto klucza API.")

    except Exception as e:
        print(f"Błąd Anime: {e}")

    return render(
        request,
        "main/events.html",
        {
            "movies": filmy,
            "games": gry,
            "anime": anime,
        },
    )