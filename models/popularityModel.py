import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
import copy


class PopularityModel:
    def __init__(self, genre_coefficient=0.5):
        self.genre_coefficient = genre_coefficient

    def fit(
        self,
        users: pd.DataFrame,
        tracks: pd.DataFrame,
        artists: pd.DataFrame,
    ) -> None:
        self.users = users
        self.tracks = tracks
        self.artists = artists

        self.users_genres = self._get_all_user_genres()
        self.artists_genres = self._get_genres_for_artist()
        self.tracks_genres = self._get_genres_for_tracks()

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
        ranked_songs = self._rank_tracks(users_genres)

        return [x["id"] for x in ranked_songs][:number_of_songs]

    def getPlaylist_with_ranks(
        self, user_ids: List[int], number_of_songs=10
    ) -> List[str]:
        self.genre_coefficient = self.genre_coefficient / len(user_ids)
        users_genres = self._aggregate_users_genres(user_ids)
        ranked_songs = self._rank_tracks(users_genres)

        return ranked_songs[:number_of_songs]

    def rank_tracks_for_users(
        self, user_ids: List[int], track_ids: List[str]
    ) -> List[str]:
        self.genre_coefficient = self.genre_coefficient / len(user_ids)
        users_genres = self._aggregate_users_genres(user_ids)
        ranked_songs = self._rank_tracks(users_genres, track_ids)

        return [x["id"] for x in ranked_songs]

    # ==================================================== ranking of the tracks

    def _rank_tracks(
        self,
        users_genres: List[Tuple[str, int]],
        track_ids=False,
    ) -> List[Tuple[str, int]]:
        if not track_ids:
            track_ids = self.tracks_genres.keys()

        ranked_tracks = []
        for track_id in track_ids:
            ranked_tracks.append(
                {
                    "id": track_id,
                    "popularity": self._calculate_popularity(
                        track_id, users_genres
                    ),
                }
            )

        return sorted(
            ranked_tracks,
            key=lambda x: x["popularity"],
            reverse=True,
        )
