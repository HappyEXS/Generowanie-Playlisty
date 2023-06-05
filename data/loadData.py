import json
import numpy as np
import pandas as pd
from typing import List, Dict
from sklearn import preprocessing
import matplotlib.pyplot as plt


def _load_file(fname) -> List[Dict]:
    with open(f"data/{fname}.jsonl", "r") as file:
        json_list = list(file)

    result = []
    for json_str in json_list:
        result.append(json.loads(json_str))
    return result


def load_users() -> pd.DataFrame:
    users = _load_file("users")
    useful_users = []
    for user in users:
        useful_users.append(
            [
                user["user_id"],
                user["premium_user"],
                user["favourite_genres"],
            ]
        )
    return pd.DataFrame(
        data=useful_users, columns=["user_id", "premium", "favourite_genres"]
    )


def load_artists() -> pd.DataFrame:
    artists = _load_file("artists")
    useful_artists = []
    for artist in artists:
        useful_artists.append([artist["id"], artist["genres"]])
    return pd.DataFrame(data=useful_artists, columns=["artist_id", "genres"])


def load_tracks(print_graphs=False) -> pd.DataFrame:
    tracks = _load_file("tracks")
    param_values = normalize_params(tracks, print_graphs)
    useful_tracks = []
    for i in range(len(tracks)):
        useful_tracks.append(
            [
                tracks[i]["id"],
                tracks[i]["popularity"],
                tracks[i]["id_artist"],
                tracks[i]["explicit"],
                [
                    param_values["duration_ms"][0][i],
                    param_values["release_date"][0][i],
                    param_values["danceability"][0][i],
                    param_values["energy"][0][i],
                    param_values["key"][0][i],
                    param_values["loudness"][0][i],
                    param_values["speechiness"][0][i],
                    param_values["acousticness"][0][i],
                    param_values["instrumentalness"][0][i],
                    param_values["liveness"][0][i],
                    param_values["valence"][0][i],
                    param_values["tempo"][0][i],
                ],
            ]
        )
    return pd.DataFrame(
        data=useful_tracks,
        columns=[
            "track_id",
            "popularity",
            "artist_id",
            "explicit",
            "params",
        ],
    )


def histogram(data, title):
    plt.clf()
    counts, bins = np.histogram(data, bins=100)
    plt.hist(bins[:-1], bins, weights=counts)

    plt.xlabel("Value")
    plt.ylabel("Frequency")
    plt.title(title)
    plt.show()


def normalize_params(tracks, print_graphs=False):
    atributes = [
        "duration_ms",
        "release_date",
        "danceability",
        "energy",
        "key",
        "loudness",
        "speechiness",
        "acousticness",
        "instrumentalness",
        "liveness",
        "valence",
        "tempo",
    ]
    param_values = {}

    for atr in atributes:
        param_values[atr] = []

    for track in tracks:
        for atr in atributes:
            if atr == "release_date":
                param_values[atr].append(int(track[atr][:4]))
            elif atr == "loudness":
                param_values[atr].append(abs(track[atr]))
            else:
                param_values[atr].append(track[atr])

    normalized_values = {}
    for atr in atributes:
        normalized_values[atr] = preprocessing.normalize([param_values[atr]])
    if print_graphs:
        for atr in atributes:
            histogram(normalized_values[atr], atr)
    return normalized_values


def load_sessions() -> pd.DataFrame:
    sessions = _load_file("sessions")
    useful_sessions = []
    for session in sessions:
        if session["event_type"] != "advertisment":
            useful_sessions.append(
                [
                    session["user_id"],
                    session["track_id"],
                    session["event_type"],
                ]
            )
    return pd.DataFrame(
        data=useful_sessions, columns=["user_id", "track_id", "event"]
    )

def load_tracks_less(print_graphs=False) -> pd.DataFrame:
    tracks = _load_file("tracks")
    param_values = normalize_params(tracks, print_graphs)
    useful_tracks = []
    for i in range(len(tracks)):
        useful_tracks.append(
            [
                tracks[i]["id"],
                tracks[i]["popularity"],
                tracks[i]["id_artist"],
                tracks[i]["explicit"],
                [
                    # param_values["duration_ms"][0][i],
                    param_values["release_date"][0][i],
                    param_values["danceability"][0][i],
                    param_values["energy"][0][i],
                    param_values["key"][0][i],
                    param_values["loudness"][0][i],
                    # param_values["speechiness"][0][i],
                    param_values["acousticness"][0][i],
                    # param_values["instrumentalness"][0][i],
                    param_values["liveness"][0][i],
                    param_values["valence"][0][i],
                    param_values["tempo"][0][i],
                ],
            ]
        )
    return pd.DataFrame(
        data=useful_tracks,
        columns=[
            "track_id",
            "popularity",
            "artist_id",
            "explicit",
            "params",
        ],
    )
