import pandas as pd
import numpy as np
from typing import List, Dict, Tuple


class TargetModel:
    def __init__(self, genre_coefficient=0.5):
        self.genre_coefficient = genre_coefficient

    def fit(
        self,
        users: pd.DataFrame,
        tracks: pd.DataFrame,
        artists: pd.DataFrame,
        sessions: pd.DataFrame,
    ) -> None:
        self.users = users
        self.tracks = tracks
        self.artists = artists
        self.sessions = sessions

        self.number_of_params = len(self.tracks.loc[0, "params"])
        self.track_vectors = {}
        for i in range(len(self.tracks)):
            self.track_vectors[
                self.tracks.loc[i, "track_id"]
            ] = self._get_vector(self.tracks.loc[i, "params"])

        self.users_genres = self._get_all_user_genres()
        self.artists_genres = self._get_genres_for_artist()
        self.tracks_genres = self._get_genres_for_tracks()

    # ==================================================== user profile functions

    def _get_vector(self, params: List) -> np.ndarray:
        return np.array(params, dtype=np.float)

    def _get_user_vector(self, user_id: int) -> np.ndarray:
        user_vector = []
        for i in range(len(self.sessions)):
            if self.sessions.loc[i, "user_id"] == user_id:
                match self.sessions.loc[i, "event"]:
                    case "play":
                        weight = 1
                    case "skip":
                        weight = -1
                    case "like":
                        weight = 2
                    case _:
                        weight = 0
                user_vector.append(
                    (
                        self.track_vectors[self.sessions.loc[i, "track_id"]],
                        weight,
                    )
                )
        return self._calculate_average_vector(user_vector)

    def _calculate_average_vector(
        self, vectors: List[Tuple[List[float], float]]
    ) -> np.ndarray:
        avg_vcector = np.zeros(shape=self.number_of_params, dtype=float)

        sum_weight = 0
        for vec in vectors:
            sum_weight += vec[1]
            avg_vcector += vec[0] * (vec[1] * np.ones(self.number_of_params))

        return avg_vcector / (sum_weight * np.ones(self.number_of_params))

    def _aggregated_users_vector(self, user_ids: List[int]) -> np.ndarray:
        user_vectors = []
        for user_id in user_ids:
            user_vectors.append(self._get_user_vector(user_id))

        avg_vcector = np.zeros(shape=self.number_of_params, dtype=float)

        for vec in user_vectors:
            avg_vcector += vec

        return avg_vcector / (
            len(user_vectors) * np.ones(self.number_of_params)
        )

    def _calculate_difference(
        self, vec1: np.ndarray, vec2: np.ndarray
    ) -> float:
        return (
            np.dot(vec1, vec2)
            / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
            * 100
        )

    # ==================================================== popularity functions

    def _get_all_user_genres(self) -> List[str]:
        all_genres = set()
        for i in range(len(self.users)):
            all_genres.update(self.users.loc[i, "favourite_genres"])
        return all_genres

    def _get_genres_for_artist(self) -> Dict:
        genres_for_artist = {}
        for i in range(len(self.artists)):
            genres_for_artist[
                self.artists.loc[i, "artist_id"]
            ] = self.artists.loc[i, "genres"]
        return genres_for_artist

    def _get_genres_for_tracks(self) -> Dict:
        tracks_with_genres = {}
        for i in range(len(self.tracks)):
            tracks_with_genres[self.tracks.loc[i, "track_id"]] = {
                "popularity": self.tracks.loc[i, "popularity"],
                "genres": self.artists_genres[self.tracks.loc[i, "artist_id"]],
            }
        return tracks_with_genres

    def _aggregate_users_genres(self, user_ids: List[int]) -> Dict:
        users_genres = {}
        for user_id in user_ids:
            for genre in self._genres_for_user(user_id):
                if genre not in users_genres:
                    users_genres[f"{genre}"] = 1
                else:
                    users_genres[f"{genre}"] += 1
        return users_genres

    def _genres_for_user(self, user_id: int) -> List[str]:
        for i in range(len(self.users)):
            if self.users.loc[i, "user_id"] == user_id:
                return self.users.loc[i, "favourite_genres"]

    def _calculate_popularity(
        self, track_id: str, users_genres: List[Tuple[str, int]]
    ) -> float:
        track_dict = self.tracks_genres[track_id]
        popularity_level = -0.1
        for genre, n_of_occurrences in list(users_genres.items()):
            if genre in track_dict["genres"]:
                popularity_level += n_of_occurrences
        return track_dict["popularity"] + (
            (
                (100 - track_dict["popularity"])
                * popularity_level
                * self.genre_coefficient
            )
        )

    # ==================================================== public methods

    def getPlaylist(self, user_ids: List[int], number_of_songs=10) -> List[str]:
        self.genre_coefficient = self.genre_coefficient / len(user_ids)
        users_genres = self._aggregate_users_genres(user_ids)
        users_vector = self._aggregated_users_vector(user_ids)

        ranked_songs = self._rank_tracks(users_genres, users_vector)
        return [x["id"] for x in ranked_songs][:number_of_songs]

    def getPlaylist_with_ranks(
        self, user_ids: List[int], number_of_songs=10
    ) -> List[str]:
        self.genre_coefficient = self.genre_coefficient / len(user_ids)
        users_genres = self._aggregate_users_genres(user_ids)
        users_vector = self._aggregated_users_vector(user_ids)

        ranked_songs = self._rank_tracks(users_genres, users_vector)
        return ranked_songs[:number_of_songs]

    def rank_tracks_for_users(
        self, user_ids: List[int], track_ids: List[str]
    ) -> List[str]:
        self.genre_coefficient = self.genre_coefficient / len(user_ids)
        users_genres = self._aggregate_users_genres(user_ids)
        users_vector = self._aggregated_users_vector(user_ids)

        ranked_songs = self._rank_tracks(users_genres, users_vector, track_ids)
        return [x["id"] for x in ranked_songs]

    # ==================================================== ranking of the tracks

    def _rank_tracks(
        self,
        users_genres: List[Tuple[str, int]],
        users_vector: np.ndarray,
        track_ids=False,
    ) -> List[Tuple[str, int]]:
        if not track_ids:
            track_ids = self.track_vectors.keys()

        ranked_tracks = []
        for track_id in track_ids:
            ranked_tracks.append(
                {
                    "id": track_id,
                    "distance": self._calculate_difference(
                        users_vector, self.track_vectors[track_id]
                    ),
                    "popularity": self._calculate_popularity(
                        track_id, users_genres
                    ),
                }
            )

        return sorted(
            ranked_tracks,
            key=lambda x: x["distance"] + x["popularity"],
            reverse=True,
        )
