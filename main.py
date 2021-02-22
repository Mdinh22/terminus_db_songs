import warnings

# Addressing a known issue regarding warnings in the TerminusDB code
# Not PEP8 friendly but the warning needs to ignored before importing
# terminusDB modules
warnings.filterwarnings("ignore", message="woqlview need "
                                          "to be used in Jupyter notebook.\n")

# Assuming that the user as pip installed terminusdb-client and
# terminusdb-client[dataframe], as well as has TerminusDB open.
from terminusdb_client import WOQLQuery, WOQLClient


def connect_server() -> WOQLClient:
    """Connects to the local server and returns a client."""
    server_url = "https://127.0.0.1:6363"
    user = "admin"
    account = "admin"
    key = "root"
    dbid = "a231songs"

    song_client = WOQLClient(server_url)
    song_client.connect(user=user, account=account, key=key, db=dbid)

    return song_client


def add_schema(song_client) -> None:
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


def add_song(song_title, song_length, song_artist,
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


def list_split(list_to_split, n) -> zip:
    """Helper function to split the list of queries into groups
    of four (song title, album, artist, length) using a generator."""
    for i in range(0, len(list_to_split), n):
        yield list_to_split[i:i + n]


def view_songs(song_client) -> None:
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


def remove_song(param, song_client) -> None:
    """Removes a song based on the entered title."""
    WOQLQuery().delete_object("doc:" + param) \
        .execute(song_client, "Deleted" + param)

    print("Removed " + param + ", if it was present.")


def edit_song_artist(title, new_artist, song_client) -> None:
    """Edits a song's artist'."""
    WOQLQuery().woql_and(
        WOQLQuery().triple("doc:" + title, "scm:artist", "v:artist"),
        WOQLQuery().delete_triple("doc:" + title, "scm:artist", "v:artist"),
        WOQLQuery().add_triple("doc:" + title, "scm:artist", new_artist),
    ).execute(song_client, "Testing edit_song")


def edit_song_album(title, new_album, song_client) -> None:
    """Edits a song's album."""
    WOQLQuery().woql_and(
        WOQLQuery().triple("doc:" + title, "scm:album", "v:album"),
        WOQLQuery().delete_triple("doc:" + title, "scm:album", "v:album"),
        WOQLQuery().add_triple("doc:" + title, "scm:album", new_album),
    ).execute(song_client, "Testing edit_song")


def edit_song_length(title, new_length, song_client) -> None:
    """Edits a song's length."""
    WOQLQuery().woql_and(
        WOQLQuery().triple("doc:" + title, "scm:length", "v:length"),
        WOQLQuery().delete_triple("doc:" + title, "scm:length", "v:length"),
        WOQLQuery().add_triple("doc:" + title, "scm:length", str(new_length)),
    ).execute(song_client, "Testing edit_song")


def edit_menu(song_client) -> None:
    """Menu for choosing which attribute to edit."""
    choice = input("Please enter a decision.\n"
                   "[1] Change a song's artist.\n"
                   "[2] Change a song's album.\n"
                   "[3] Change a song's length.\n")

    if int(choice) == 1:
        song_title = input("Please enter the song title. ")

        new_artist = input("Please enter the new artist.")
        edit_song_artist(song_title, new_artist, song_client)

    elif int(choice) == 2:
        song_title = input("Please enter the song title. ")

        new_album = input("Please enter the new album. ")
        edit_song_album(song_title, new_album, song_client)

    elif int(choice) == 3:
        song_title = input("Please enter the song title. ")
        new_length = 0
        positive_integer = False
        while not positive_integer:
            str_new_length = input("Please enter the new length, as a positive "
                                   "integer representing the length "
                                   "of the song in seconds. ")
            new_length = int(str_new_length)

            if int(new_length) > 0:
                positive_integer = True

        edit_song_length(song_title, new_length, song_client)


def add_menu(song_client) -> None:
    """Series of prompts to add a song."""
    name = input("Please enter the song's name. ")
    artist = input("Please enter the artist. ")
    album = input("Please enter the album. ")
    length = input("Please enter the length. ")

    add_song(name, length, artist, album, song_client)


def remove_menu(song_client) -> None:
    """Prompt for singular removal of a song."""
    song_to_remove = input("Please enter a song title "
                           "to remove from the database: ")

    remove_song(song_to_remove, song_client)


def main_menu(song_client) -> None:
    """Main menu for user to choose actions."""
    finished = False
    while not finished:
        choice = input("Please enter a decision.\n"
                       "[1] View Songs in Database.\n"
                       "[2] Add a song.\n"
                       "[3] Remove a song.\n"
                       "[4] Edit a song.\n"
                       "[5] Exit.\n")

        if int(choice) == 1:
            view_songs(song_client)
        elif int(choice) == 2:
            add_menu(song_client)
        elif int(choice) == 3:
            remove_menu(song_client)
        elif int(choice) == 4:
            edit_menu(song_client)
        elif int(choice) == 5:
            finished = True


if __name__ == "__main__":
    client = connect_server()
    main_menu(client)
