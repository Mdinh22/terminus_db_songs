import warnings
import urllib.request
import urllib.error
import os
import time

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
# Ignoring pygame welcome message
import pygame

# Addressing a known issue regarding warnings in the TerminusDB code
# Not PEP8 friendly but the warning needs to ignored before importing
# terminusDB modules
warnings.filterwarnings("ignore", message="woqlview need "
                                          "to be used in Jupyter notebook.\n")

# Assuming that the user as pip installed terminusdb-client and
# terminusdb-client[dataframe], as well as has TerminusDB open and
# access to the a231songs database.
from terminusdb_client import WOQLQuery, WOQLClient


def connect_server() -> WOQLClient:
    """Connects to the local server and returns a client."""
    server_url = "https://127.0.0.1:6363"
    user = "admin"
    account = "admin"
    key = "root"
    dbid = "a231_songs_features"

    song_client = WOQLClient(server_url)
    song_client.connect(user=user, account=account, key=key, db=dbid)

    return song_client


# Assertion commented out to save memory.
# assertion_server = WOQLClient("https://127.0.0.1:6363")
# assertion_server.connect(user="admin", account="admin",
# key="root", dbid="a231songs")
# assert(assertion_server.server()== "https://127.0.0.1:6363/")


def add_schema(song_client: WOQLClient) -> None:
    """Creates and adds the schema, if it is not already added.
    Safe to attempt to add repeatedly, since it is idempotent."""
    WOQLQuery().woql_and(
        WOQLQuery().doctype("scm:Song")
        .label("Song")
        .description("A song title.")
        .cardinality(1)
        .property("scm:artist", "xsd:string")
        .label("artist")
        .cardinality(1)
        .property("scm:length", "xsd:string")
        .label("song length")
        .property("scm:album", "xsd:string")
        .label("album")
    ).execute(song_client, "Adding song object to schema")


def add_song(song_title: str, song_length: str, song_artist: str,
             song_album, song_client) -> None:
    """Adds a song to the database."""
    message = "Added: " + song_title + "\n"

    query = WOQLQuery().woql_and(
        WOQLQuery().insert("doc:" + str(song_title), "scm:Song")
        .property("scm:artist", str(song_artist))
        .property("scm:length", str(song_length))
        .property("scm:album", str(song_album))
    )
    query.execute(song_client, message)

    print(message)


def view_songs(song_client: WOQLClient) -> None:
    """Prints out the songs in the database."""
    song_query = WOQLQuery() \
        .limit(100) \
        .triple("v:song_length", "v:artist", "v:album").execute(song_client)

    query_results = song_query.get("bindings")
    zip_of_queries = zip(*(iter(query_results),) * 4)
    list_of_queries = list(zip_of_queries)

    print("Songs in Database:\n")
    for query in list_of_queries:
        print("Song Name: " + query[0]['song_length'].split("data/")[1])
        print("Song Album: " + query[1]['album']['@value'])
        print("Song Artist: " + query[2]['album']['@value'])
        print("Song Length: " + str(query[3]['album']['@value']))
        print()


def remove_song(song_to_remove: str, song_client: WOQLClient) -> None:
    """Removes a song based on the entered title."""
    WOQLQuery().delete_object("doc:" + song_to_remove) \
        .execute(song_client, "Deleted" + song_to_remove)

    print("Removed " + song_to_remove + ", if it was present.")


def edit_song_artist(title: str, new_artist: str,
                     song_client: WOQLClient) -> None:
    """Edits a song's artist'."""
    WOQLQuery().woql_and(
        WOQLQuery().triple("doc:" + title, "scm:artist", "v:artist"),
        WOQLQuery().delete_triple("doc:" + title, "scm:artist", "v:artist"),
        WOQLQuery().add_triple("doc:" + title, "scm:artist", new_artist),
    ).execute(song_client, "Testing edit_song")


def edit_song_album(title: str, new_album: str,
                    song_client: WOQLClient) -> None:
    """Edits a song's album."""
    WOQLQuery().woql_and(
        WOQLQuery().triple("doc:" + title, "scm:album", "v:album"),
        WOQLQuery().delete_triple("doc:" + title, "scm:album", "v:album"),
        WOQLQuery().add_triple("doc:" + title, "scm:album", new_album),
    ).execute(song_client, "Testing edit_song")


def edit_song_length(title: str, new_length: int,
                     song_client: WOQLClient) -> None:
    """Edits a song's length."""
    WOQLQuery().woql_and(
        WOQLQuery().triple("doc:" + title, "scm:length", "v:length"),
        WOQLQuery().delete_triple("doc:" + title, "scm:length", "v:length"),
        WOQLQuery().add_triple("doc:" + title, "scm:length", str(new_length)),
    ).execute(song_client, "Testing edit_song")


def edit_menu(song_client: WOQLClient) -> None:
    """Menu for choosing which attribute to edit."""
    choice = input("Please enter a decision.\n"
                   "[1] Change a song's artist.\n"
                   "[2] Change a song's album.\n"
                   "[3] Change a song's length.\n")

    while True:
        if int(choice) == 1:
            song_title = input("Please enter the song title. ")

            new_artist = input("Please enter the new artist.")
            edit_song_artist(song_title, new_artist, song_client)
            break

        elif int(choice) == 2:
            song_title = input("Please enter the song title. ")

            new_album = input("Please enter the new album. ")
            edit_song_album(song_title, new_album, song_client)
            break

        elif int(choice) == 3:
            song_title = input("Please enter the song title. ")
            new_length = 0
            positive_integer = False
            while not positive_integer:
                str_new_length = input("Please enter the new length, as a "
                                       "positive integer representing "
                                       "the length "
                                       "of the song in seconds. ")
                new_length = int(str_new_length)

                if int(new_length) > 0:
                    positive_integer = True

            edit_song_length(song_title, new_length, song_client)
            break
        else:
            print("The option that you have inputted is invalid. Try again.")


def add_menu(song_client: WOQLClient) -> None:
    """Series of prompts to add a song."""
    name = input("Please enter the song's name. ")
    album = input("Please enter the album. ")
    artist = input("Please enter the artist. ")
    length = input("Please enter the length. ")

    add_song(name, length, artist, album, song_client)


def remove_menu(song_client: WOQLClient) -> None:
    """Prompt for singular removal of a song."""
    song_to_remove = input("Please enter a song title "
                           "to remove from the database: ")

    remove_song(song_to_remove, song_client)


def find_menu(song_client: WOQLClient) -> None:
    song_query = WOQLQuery() \
        .limit(100) \
        .triple("v:song_length", "v:artist", "v:album").execute(song_client)

    query_results = song_query.get("bindings")
    zip_of_queries = zip(*(iter(query_results),) * 4)
    list_of_queries = list(zip_of_queries)

    while True:
        choice = input("What category do you want to search by?\n"
                       "[1] Search by song name.\n"
                       "[2] Search by song album.\n"
                       "[3] Search by song artist.\n"
                       "[4] Search by song length.\n")
        if int(choice) == 1:
            song_name = input("Enter the name of the song that you are"
                              "searching for: ")
            list_of_indexes = []
            index = 0
            for query in list_of_queries:
                if song_name == query[0]['song_length'].split("data/")[1]:
                    list_of_indexes.append(index)
                index += 1

            print("\nFound {0} instance(s) of the song {1} in the Database\n"
                  .format(str(len(list_of_indexes)), song_name))
            for index in list_of_indexes:
                print("Song Name: " + list_of_queries[index][0]['song_length']
                      .split("data/")[1])
                print("Song Album: " +
                      list_of_queries[index][1]['album']['@value'])
                print("Song Artist: " +
                      list_of_queries[index][2]['album']['@value'])
                print("Song Length: " +
                      str(list_of_queries[index][3]['album']['@value']))
                print()

            break

        elif int(choice) == 2:
            song_album = input("Enter the album of the song that you are"
                               "searching for: ")
            list_of_indexes = []
            index = 0
            for query in list_of_queries:
                if song_album == query[1]['album']['@value']:
                    list_of_indexes.append(index)
                index += 1

            print("\nFound " + str(len(list_of_indexes)) +
                  " instance(s) of the album" + song_album +
                  " in the Database\n")
            for index in list_of_indexes:
                print("Song Name: " +
                      list_of_queries[index][0]['song_length']
                      .split("data/")[1])
                print("Song Album: " +
                      list_of_queries[index][1]['album']['@value'])
                print("Song Artist: " +
                      list_of_queries[index][2]['album']['@value'])
                print("Song Length: " +
                      str(list_of_queries[index][3]['album']['@value']))
                print()

            break

        elif int(choice) == 3:
            song_artist = input("Enter the artist of the song that you are"
                                "searching for: ")
            list_of_indexes = []
            index = 0
            for query in list_of_queries:
                if song_artist == query[2]['album']['@value']:
                    list_of_indexes.append(index)
                index += 1

            print("\nFound " + str(len(list_of_indexes)) +
                  " instance(s) of the artist " + song_artist +
                  " in the Database\n")
            for index in list_of_indexes:
                print("Song Name: " +
                      list_of_queries[index][0]['song_length']
                      .split("data/")[1])
                print("Song Album: " +
                      list_of_queries[index][1]['album']['@value'])
                print("Song Artist: " +
                      list_of_queries[index][2]['album']['@value'])
                print("Song Length: " +
                      str(list_of_queries[index][3]['album']['@value']))
                print()

            break

        elif int(choice) == 4:
            song_length = input("Enter the length of the song that you are"
                                "searching for: ")
            list_of_indexes = []
            index = 0
            for query in list_of_queries:
                if int(song_length) == query[3]['album']['@value']:
                    list_of_indexes.append(index)
                index += 1

            print("\nFound " + str(len(list_of_indexes)) +
                  " instance(s) of length " + song_length +
                  " in the Database\n")
            for index in list_of_indexes:
                print("Song Name: " +
                      list_of_queries[index][0]['song_length']
                      .split("data/")[1])
                print("Song Album: " +
                      list_of_queries[index][1]['album']['@value'])
                print("Song Artist: " +
                      list_of_queries[index][2]['album']['@value'])
                print("Song Length: " +
                      str(list_of_queries[index][3]['album']['@value']))
                print()

            break

        else:
            print("The option that you have inputted is invalid. Try again.")


def play_song() -> None:
    """Downloads and plays a song based on the entered title,
    if it is hosted on project github."""
    while(True):
        song_to_play = input("Enter a song title to be played. "
                             "It must be hosted on "
                             "this project's github and in .wav format. ")
        for query in list_of_queries:
                if song_to_play == query[0]['song_length'].split("data/")[1]:
                    break
    
        print("The song that you are looking for is not in the database")

    host_url = "https://raw.githubusercontent.com" \
               "/Mdinh22/terminus_db_songs/main/"

    try:
        print("Attempting to download and play the file...\n")
        url = host_url + song_to_play + ".wav"
        urllib.request.urlretrieve(url, song_to_play + ".wav")

        pygame.mixer.init()
        pygame.mixer.music.load(song_to_play + ".wav")
        pygame.mixer.music.set_volume(0.7)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(1)
    except urllib.error.HTTPError:
        print("File could not be found! Are you sure the file"
              "is hosted on the github and the name is correct?")


def main_menu(song_client: WOQLClient) -> None:
    """Main menu for user to choose actions."""
    while True:
        choice = input("Please enter a decision.\n"
                       "[1] View Songs in Database.\n"
                       "[2] Add a song.\n"
                       "[3] Remove a song.\n"
                       "[4] Edit a song.\n"
                       "[5] Find a song.\n"
                       "[6] Download/Play a song\n"
                       "[7] Exit.\n")

        if int(choice) == 1:
            view_songs(song_client)
        elif int(choice) == 2:
            add_menu(song_client)
        elif int(choice) == 3:
            remove_menu(song_client)
        elif int(choice) == 4:
            edit_menu(song_client)
        elif int(choice) == 5:
            find_menu(song_client)
        elif int(choice) == 6:
            play_song()
        elif int(choice) == 7:
            break
        else:
            print("The option that you have inputted is invalid. Try again.")


if __name__ == "__main__":
    client = connect_server()
    main_menu(client)
