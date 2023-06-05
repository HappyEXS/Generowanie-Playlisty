import json
import os.path
from typing import List
from datetime import datetime

from models.userProfileModel import UserProfileModel
from models.popularityModel import PopularityModel
from models.targetModel import TargetModel
from data.dataFunctions import (
    get_played_songs_for_user_id,
    get_songs_by_traks_ids,
)
from data.loadData import load_users, load_tracks, load_artists, load_sessions

# Global scope variables
base_model: UserProfileModel
target_model: TargetModel
log_filename = "log.json"
sessions: List
default_session_id = 60000

# from witch user_id the base model will create playlist
split_A_B = 300


def display_welcome_banner():
    print("#" * 50)
    print(f'#{" " * 16}Client Interface{" " * 16}#')
    print("#" * 50)
    print()


def display_main_menu():
    print("Choose one of the below actions:")
    print("\t1. Get new playlist")
    print("\t2. See song history")
    print("\t3. Log out")


def get_users_choice() -> int:
    try:
        choice = int(input("Your choice (1-3): "))
    except ValueError:
        choice = 0
    return choice


def get_users_id() -> int:
    while True:
        try:
            user_id = int(input("Enter user id (or 0 to finish): "))
            if user_id == 0:
                return 0
            elif user_id in range(101, 601):
                return user_id
            else:
                print("Unknown user id. Please try again.")
        except ValueError:
            print("Unknown user id. Please try again.")


def display_history(user_id: int):
    print("Loading...")
    songs = get_played_songs_for_user_id(user_id, sessions)
    print(f"User's (id={user_id}) song history:")
    for song in songs:
        print(f'\t* {song}')
    print(f"User (id={user_id}) listened to {len(songs)} songs")
    print()
    print("*" * 30)
    print()


def play_new_playlist(user_id: int, session_id: int):

    print("*** Add more users to your playlist ***")
    users = {user_id}
    while True:
        user = get_users_id()
        if user == 0:
            break
        users.add(user)
    print("\nCreating the playlist...")
    # choosing model for generating playlist
    if user_id > split_A_B:
        songs = base_model.getPlaylist(list(users))
        model_type = "base"
    else:
        songs = target_model.getPlaylist(list(users))
        model_type = "target"

    display_playlist(songs, user_id, session_id, model_type)


def display_playlist(songs, user_id, session_id, model_type):
    songs_names = get_songs_by_traks_ids(songs)
    log = list(dict())
    for i in range(0, len(songs)):
        print(f'Song proposition: "{songs_names[i]}"')
        print("Choose what you want to do with the song:")
        print("\t1. Like")
        print("\t2. Play")
        print("\t3. Skip")
        choice = get_users_choice()
        while choice not in range(1, 4):
            print("Incorrect input. Please try again.")
            choice = get_users_choice()
        if choice == 1:
            event_type = "like"
        elif choice == 2:
            event_type = "play"
        else:
            event_type = "skip"
        timestamp = datetime.fromtimestamp(
            datetime.timestamp(datetime.now())
        ).strftime("%Y-%m-%dT%H:%M:%S.%f")
        log.append(
            {
                "session_id": session_id,
                "timestamp": timestamp,
                "user_id": user_id,
                "track_id": songs[i],
                "event_type": event_type,
                "model_type": model_type,
            }
        )
    print("\n*** End of the playlist ***\n")
    with open(log_filename, "a") as file:
        for entry in log:
            json.dump(entry, file)
            file.write("\n")


def initialize_models():
    global base_model, target_model, sessions
    print("Loading...")

    users = load_users()
    tracks = load_tracks()
    artists = load_artists()
    sessions = load_sessions()

    base_model = UserProfileModel()
    base_model.fit(users, tracks, sessions)

    target_model = TargetModel()
    target_model.fit(users, tracks, artists, sessions)


def initialize_session_id():
    session_id = default_session_id
    if os.path.isfile(log_filename):
        with open(log_filename, "r") as file:
            # getting last session_id from log
            session_id = int(list(file)[-1].split()[1][:-1]) + 1
    return session_id


def main():
    display_welcome_banner()

    initialize_models()
    session_id = initialize_session_id()

    logged_in = False
    while not logged_in:
        user_id = get_users_id()
        if user_id == 0:
            exit()
        logged_in = True

        while logged_in:
            display_main_menu()
            choice = get_users_choice()
            while choice not in range(1, 4):
                print("Incorrect input. Please try again.")
                choice = get_users_choice()
            if choice == 1:
                play_new_playlist(user_id, session_id)
            elif choice == 2:
                display_history(user_id)
            else:
                logged_in = False
                print("\nYou have been logged out\n")
        session_id += 1


if __name__ == "__main__":
    main()
