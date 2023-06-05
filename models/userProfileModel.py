import pandas as pd
import numpy as np
from typing import List, Dict, Tuple


class UserProfileModel:
    def __init__(self) -> None:
        pass

    def fit(
        self, users: pd.DataFrame, tracks: pd.DataFrame, sessions: pd.DataFrame
    ) -> None:
        self.users = users
        self.tracks = tracks
        self.sessions = sessions
        self.number_of_params = len(self.tracks.loc[0, "params"])
        self.track_vectors = {}
        for i in range(len(self.tracks)):
            self.track_vectors[
                self.tracks.loc[i, "track_id"]
            ] = self._get_vector(self.tracks.loc[i, "params"])

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

    def _aggregate_user_vectors(
        self, user_vectors: List[np.ndarray]
    ) -> np.ndarray:
        avg_vcector = np.zeros(shape=self.number_of_params, dtype=float)

        for vec in user_vectors:
            avg_vcector += vec

        return avg_vcector / (
            len(user_vectors) * np.ones(self.number_of_params)
        )

    def _find_best_tracks(
        self, vector: np.ndarray, number_of_songs: int
    ) -> List[str]:
        vector_difference = []
        for i in range(len(self.tracks)):
            vector_difference.append(
                (
                    self._calculate_difference(
                        vector, self._get_vector(self.tracks.loc[i, "params"])
                    ),
                    self.tracks.loc[i, "track_id"],
                )
            )
        return sorted(vector_difference, key=lambda x: x[0], reverse=True)[
            :number_of_songs
        ]

    def _calculate_difference(
        self, vec1: np.ndarray, vec2: np.ndarray
    ) -> float:
        return np.dot(vec1, vec2) / (
            np.linalg.norm(vec1) * np.linalg.norm(vec2)
        )

    def _rank_tracks_for_vector(
        self, users_vector: np.ndarray, track_ids: List[str]
    ) -> List[str]:
        vector_difference = []
        for track_id in track_ids:
            vector_difference.append(
                (
                    self._calculate_difference(
                        users_vector, self.track_vectors[track_id]
                    ),
                    track_id,
                )
            )
        return sorted(vector_difference, key=lambda x: x[0], reverse=True)

    # ==================================================== public methods

    def getPlaylist(self, user_ids: List[int], number_of_songs=10) -> List[str]:
        user_vectors = []
        for user_id in user_ids:
            user_vectors.append(self._get_user_vector(user_id))

        aggregated_vector = self._aggregate_user_vectors(user_vectors)
        tracks_in_order = self._find_best_tracks(
            aggregated_vector, number_of_songs
        )
        return [x[1] for x in tracks_in_order]

    def getPlaylist_with_ranks(
        self, user_ids: List[int], number_of_songs=10
    ) -> List[str]:
        user_vectors = []
        for user_id in user_ids:
            user_vectors.append(self._get_user_vector(user_id))

        aggregated_vector = self._aggregate_user_vectors(user_vectors)
        tracks_in_order = self._find_best_tracks(
            aggregated_vector, number_of_songs
        )
        return tracks_in_order

    def rank_tracks_for_users(
        self, user_ids: List[int], track_ids: List[str]
    ) -> List[str]:
        user_vectors = []
        for user_id in user_ids:
            user_vectors.append(self._get_user_vector(user_id))

        aggregated_vector = self._aggregate_user_vectors(user_vectors)
        tracks_in_order = self._rank_tracks_for_vector(
            aggregated_vector, track_ids
        )
        return [x[1] for x in tracks_in_order]
