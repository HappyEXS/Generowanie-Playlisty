from data.loadData import _load_file, load_tracks
from typing import List
import pandas as pd
import numpy as np


def get_played_songs_for_user_id(
    user_id: int, sessions: pd.DataFrame
) -> List[str]:
    songs = {}
    tracks = _load_file("tracks")
    artists = _load_file("artists")
    for i in range(len(sessions)):
        if sessions.loc[i, "event"] != "advertisment":
            if sessions.loc[i, "user_id"] == user_id:
                if sessions.loc[i, "track_id"] not in songs:
                    songs[sessions.loc[i, "track_id"]] = 1
                else:
                    songs[sessions.loc[i, "track_id"]] += 1

    song_names = []
    for song in songs:
        song_names.append(get_song_name_artist(song, tracks, artists))

    return song_names


def get_played_tracks(user_ids: List[int], sessions: List) -> List[str]:
    songs = set()
    for i in range(len(sessions)):
        if sessions.loc[i, "user_id"] in user_ids:
            songs.add(sessions.loc[i, "track_id"])

    return list(songs)


def get_song_name_artist(track_id: str, tracks: List, artists: List) -> str:
    for track in tracks:
        if track["id"] == track_id:
            for artist in artists:
                if artist["id"] == track["id_artist"]:
                    return '"' + track["name"] + '" - ' + artist["name"]


def get_songs_by_traks_ids(track_ids: List[str]) -> List[str]:
    tracks = _load_file("tracks")
    artists = _load_file("artists")
    return [
        get_song_name_artist(track_id, tracks, artists)
        for track_id in track_ids
    ]


def find_random_n_track_ids(n_of_tracks: int) -> List[str]:
    tracks = load_tracks()
    return np.random.choice(tracks["track_id"], size=n_of_tracks)


def get_tracks_dataset(track_ids: List[str]) -> pd.DataFrame:
    pass
