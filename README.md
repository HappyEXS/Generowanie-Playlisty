# Projekt z przedmiotu: Inżynieria Uczenia Maszynowego
Jan Jędrzejewski - 21.01.2023r.

## Temat projektu

“Może bylibyśmy w stanie wygenerować playlistę, która spodoba się kilku wybranym
osobom jednocześnie? Coraz więcej osób używa Aplikacji podczas różnego rodzaju
imprez i taka funkcjonalność byłaby hitem!”

## Dane
Bazujemy na czterech plikach z zebranymi danymi z aplikacji
- `artists`: ogólne informacje o artystach: imię/nazwa, gatunki muzyczne
- `tracks`: dane o utworach dostępnych w serwisie - oprócz podstawowych tytułów i wykonawców mamy szereg parametrów takich jak: długość, głośność, poziom energii/akustyczności, ton a także ranking popularności
- `users`: ogólne informacje o użytkownikach - miejsce zamieszkania, data urodzenia, ulubione gatunki muzyczne
- `sessions`: logi sesji użytkowników - dla każdej sesji zarejestrowane interakcje użytkownika (np. wysłuchanie piosenki, polubienie/pominięcie piosenki)

## Etap 1
W ramach etapu pierwszego wytworzono dokumentację oraz notebooki w folderze etap1. Zamieszczono podstawowe obserwacje i analizę otrzymanych danych od klienta.

## Etap 2
Na drugi etap stworzono modele predyktujące piosenki które użytkownicy najchętniej by wysłuchali. Zamieszczono przykładowe działanie i porównanie modeli. Stworzono aplikację tekstową która korzysta z modeli i tworzy playlisty dla użytkowników.

# Modele

W folderze models zamieszczono kody źródłowe trzech modeli rankngującyh do tworzenia playlist. Na wejściu pobierają listę id użytkowników dla których generują listę piosenek o długości n. Modele tak naprawdę rankingują piosenki i na podstawie kryteriów rankingują piosenki w skali od 0 do 100. N utworów z najlepszym rankingiem zostaje wybranych do playlisty.

## Model popularności - popularityModel.py
Na podstawie popularności (popularity utworu) oraz ulubionych gatunków muzycznych użytkowników (które są przypisane też do artystów) rankingujemy piosenki w zbiorze.

## Model parametrów utworów - userProfileModel.py
Dla użytkownika tworzymy wektor ulubionej charakterystyki utworu na podstawie posenek których wcześniej wysłuchał i jego reakcji (polibień i pominięć). Porównuje średni wektor użytkownika z utworami ze zbioru i wybiera najbardziej podobne.

## Model docelowy - targetModel.py
Łączy dwa poprzednie koncepty w jeden model. Obie metody w proporcjach 50/50. Kożysta ze wszystkich dostępnych danych.

## Kożystanie z modeli

Przykładowe wykorzystanie modeli jest zaprezentowane w notebookach `test-<nazwaModely>.ipynb`

## Porównanie modeli

Zestawienie rankingowania modeli oraz porównanie znajduje się w pliku `evaluation.ipynb`

# Aplikacja

W ramach projektu stworzono aplikację `app.py` symulującą działąnie modeli w środowisku z użytkownikami.

### Uruchomienie aplikacji
```shell
python app.py
```
### Logi z sesji w aplikacji

W pliku `log.json` zapisywane są logi sesji użytkowników z aplikacji
