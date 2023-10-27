import json
import datetime
import random
from DB import Database
start_datetime = datetime.datetime(2018, 1, 1, 0, 0, 0)     # January 1, 2018 at 12:00:00 AM
end_datetime = datetime.datetime(2022, 12, 31, 23, 59, 59)  # December 31, 2022 at 11:59:59 PM
possible_genre_combinations = [ 
    ["Rap"], ["Reggae"], ["Country"], 
    ["Pop"], ["RnB"], ["Classical"], 
    ["Electronic"], ["Rock"], ["Funk"], 
    ["Rap", "Reggae"], ["Rap", "RnB"], 
    ["Electronic", "Pop"], ["Electronic", "Funk"], 
    ["Pop", "Rock"] 
]

max_n_genres = max([len(i) for i in possible_genre_combinations])
genre_combinations_len_map = {i : [t for t in possible_genre_combinations if len(t) == i] for i in range(1, max_n_genres + 1)}
# Get a randomly generated integer in [0, max_size] from right skewed distribution (1 -> 0.5, 2 -> 0.25, 3 -> 0.125, ... , max_size -> ~0)
def random_ls_size(max_size):
    sum_freqs = (2 ** max_size - 1) / 2 ** max_size                     # Divisor to normalize frequencies, so they sum to 1
    ls_size_freqs = [(i + 1, (1 / (2 ** (i + 1))) / sum_freqs) for i in range(max_size)]
    total = 0
    ls_len = None
    rval = random.random()
    for len, freq in ls_size_freqs:
        total += freq
        if rval < total:
            ls_len = len
            break
    if ls_len is None: ls_len = max_size
    return ls_len

# Get a random sublist from a list (using random_ls_size() to get list size)
def random_ls(sample_ls):
    ls_size = random_ls_size(len(sample_ls))
    ls = []
    seen = set()
    for i in range(ls_size):
        while True:
            elem = random.choice(sample_ls)
            if elem not in seen:
                ls.append(elem)
                seen.add(elem)
                break
    return ls

# Random datetime from uniform distribution
def random_datetime(start=start_datetime, end=end_datetime):
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = random.randrange(int_delta)
    return start + datetime.timedelta(seconds=random_second)

# Random date from uniform distribution
def random_date(start=start_datetime, end=end_datetime):
    return random_datetime(start=start_datetime, end=end_datetime).date()

# Convert a python datetime to an sql datetime
def python_datetime_to_sql(python_dt : datetime.datetime):
    f = '%Y-%m-%d %H:%M:%S'
    return python_dt.strftime(f)

# Convert a python date to an sql date
def python_date_to_sql(python_d : datetime.date):
    f = '%Y-%m-%d'
    y, m, d = python_d.year, python_d.month, python_d.day
    python_dt = datetime.datetime(y, m, d, 0, 0)
    return python_dt.strftime(f)

if __name__ == "__main__":

    # Get login
    with open("login.json") as f:
        credentials = json.loads(f.read())
        login = (credentials['username'], credentials['password'])

    # Load project database
    db = Database(login[0], login[1])

    # Load attributes
    with open("songs.txt") as f: songs = [l.strip() for l in f.readlines()]
    with open("artists.txt") as f: artists = [l.strip() for l in f.readlines()]
    with open("genres.txt") as f: genres = [l.strip() for l in f.readlines()]

    # ID -> Attribute maps
    song_id_map = dict()
    n_songs = 0
    artist_id_map = dict()
    n_artists = 0
    genre_id_map = dict()
    n_genres = 0
    
    #queries = []
    # Add Genre rows
    for genre_name in genres:
    
        # Get new genre id
        genre_id = n_genres
        genre_id_map[genre_name] = genre_id
        n_genres += 1
        
        # Add genre to database
        query = "insert into Genre (GenreID, Name) values ({}, \"{}\");".format(genre_id, genre_name)
        #queries.append(query)
        db.query(query)
    
    # Add Song, Artist, Album (single entry), AlbumContains, AlbumGenre, SongGenre, SongBy rows
    for song_name in songs:
        
        # Get new song id
        song_id = n_songs
        song_id_map[song_name] = song_id
        n_songs += 1
        
        # Get song duration from uniform distribution (120 - 300)
        song_duration = int(random.uniform(120, 300.01))
        
        # Get song date from uniform distribution (01/01/2018 - 12/31/2022)
        song_date = random_date()
        
        # Get random list of genres
        ls_size = random_ls_size(max_n_genres)
        genres = random.choice(genre_combinations_len_map[ls_size])
        genre_ids = [genre_id_map[genre] for genre in genres]
        
        # Get random list of artists (adding artist to database if necessary)
        artists = random_ls(artists)
        artist_ids = []
        for artist in artists:
            if artist not in artist_id_map:             # Add artists to database
                
                # Get new artist id
                artist_id = n_artists
                artist_id_map[artist] = artist_id
                n_artists += 1
                
                # Add artist to database
                query = "insert into Artist (ArtistID, Name) values ({}, \"{}\");".format(artist_id, artist)
                #queries.append(query)
                db.query(query)
                
            else:                                       # Artist already in database
                artist_id = artist_id_map[artist]
            artist_ids.append(artist_id)
            
        # Add Song to database
        query = "insert into Song (SongID, Length, Title, ReleaseDate) values ({}, {}, \"{}\", {});".format(song_id, song_duration, song_name, python_date_to_sql(song_date))
        #queries.append(query)
        db.query(query)
        
        # Add SongGenre to database
        for genre_id in genre_ids:
            query = "insert into SongGenre (SongID, GenreID) values ({}, {});".format(song_id, genre_id)
            #queries.append(query)
            db.query(query)
        
        # Add SongBy to database
        for artist_id in artist_ids:
            query = "insert into SongBy (SongID, ArtistID) values ({}, {});".format(song_id, artist_id)
            #queries.append(query)
            db.query(query)
        
        # Add Album to database
        album_id = song_id
        album_name = song_name
        album_date = song_date
        query = "insert into Album (AlbumID, Name, ReleaseDate) values ({}, \"{}\", {});".format(album_id, album_name, python_date_to_sql(album_date))
        #queries.append(query)
        db.query(query)
        
        # Add AlbumContains to database (album containing solely this song, w/ track number 1)
        track_no = 1
        query = "insert into AlbumContains (AlbumID, SongID, TrackNumber) values ({}, {}, {});".format(album_id, song_id, track_no)
        #queries.append(query)
        db.query(query)
        
        # Add AlbumGenre to database
        for genre_id in genre_ids:
            query = "insert into AlbumGenre (AlbumID, GenreID) values ({}, {});".format(album_id, genre_id)
            #queries.append(query)
            db.query(query)

"""    
    # Write queries to text file
    with open("queries.txt", 'w') as f:
        for query in queries:
            f.write(query + '\n')
"""