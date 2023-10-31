import json
import datetime
import random
from database import Database
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



# Generate 2^-i frequency distribution for i in [1:size]
# n(i) > 2 * n(i + 1) for all 1 <= i <= size
# n(i) != 0 for all 1 <= i <= size
# sum({n(i) for all 1 <= i <= size}) = 1
# limit size -> inf for get_inv2_frequencies(size) = [0.5, 0.25, 0.125, ...]
def get_inv2_frequencies(size):
    freqs = []
    norm = (2 ** size - 1) / 2 ** size
    for i in range(size):
        freq = 2 ** -(i + 1)
        freqs.append(freq / norm)
    return freqs

# Return an index given a list of frequencies for each index
# Sum of freqs should be 1
# freq(i) is the probability of i
def random_index_freq(freqs):
    total = 0
    rval = random.random()
    for i in range(len(freqs)):
        total += freqs[i]
        if rval < total:
            return i
    return len(freqs) - 1


# Return random disjoint subsets of a given list with size specified upon call
# List will be modified
def random_subset_without_replacement(ls, min_size, max_size, size_freqs = None):
    if size_freqs is not None: assert max_size - min_size == len(size_freqs) + 1
    random.shuffle(ls)
    i = 0
    while i < len(ls):
        size = random.randint(min_size, max_size) if size_freqs is None else random_index_freq(size_freqs) + min_size
        yield ls[i : i + size]
        i += size

# Return random subsets of a given list
def random_subset_with_replacement(ls, min_size, max_size, size_freqs = None):
    if size_freqs is not None: assert max_size - min_size == len(size_freqs) + 1
    while True:
        size = random.randint(min_size, max_size) if size_freqs is None else random_index_freq(size_freqs) + min_size
        yield random.choices(ls, k=size)


max_n_genres = max([len(i) for i in possible_genre_combinations])
genre_combinations_len_map = {i : [t for t in possible_genre_combinations if len(t) == i] for i in range(1, max_n_genres + 1)}

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
    
    # Sizes
    min_n_album_songs = 1
    max_n_album_songs = 12
    min_n_album_artists = 1
    max_n_album_artists = 3
    
    # Id maps
    n_albums = 0
    n_songs = 0
    artist_id_map = dict()
    n_artists = 0
    genre_id_map = dict()
    n_genres = 0
    
    # Get login
    with open("login.json") as f:
        credentials = json.loads(f.read())
        login = (credentials['username'], credentials['password'])

    # Load project database
    db = Database(login[0], login[1])
    queries = []

    # Load attributes
    with open("songs.txt") as f: songs = [l.strip().replace("'", "") for l in f.readlines() if len(l) <= 60]
    with open("artists.txt") as f: artists = [l.strip().replace("'", "") for l in f.readlines() if len(l) <= 60]
    with open("genres.txt") as f: genres = [l.strip() for l in f.readlines()]
    
    # Add Genre rows
    for genre_name in genres:
    
        # Get new genre id
        genre_id = n_genres
        genre_id_map[genre_name] = genre_id
        n_genres += 1
        
        # Add genre to database
        query = "insert into genre (genreid, name) values ({}, \'{}\');".format(genre_id, genre_name)
        queries.append(query)
        db.query(query)
    
    album_songs_generator = random_subset_without_replacement(songs, min_n_album_songs, max_n_album_songs)
    album_artists_generator = random_subset_with_replacement(artists, min_n_album_artists, max_n_album_artists, size_freqs = get_inv2_frequencies(max_n_album_artists - min_n_album_artists - 1))
    for album_songs in album_songs_generator.__iter__():
        album_artists = album_artists_generator.__next__()
        album_genres = random.choice(possible_genre_combinations)
        album_name = random.choice(album_songs)
        album_date = python_date_to_sql(random_date())
        album_id = n_albums
        n_albums += 1
        
        artist_ids = []
        for artist in album_artists:
            
            # Add new artist
            if artist not in artist_id_map:
                
                # Get new artist id
                artist_id = n_artists
                artist_id_map[artist] = artist_id
                n_artists += 1
                
                # Add artist to database
                query = "insert into artist (artistid, name) values ({}, \'{}\');".format(artist_id, artist)
                queries.append(query)
                db.query(query)
                
            artist_id = artist_id_map[artist]
            
        # Add each song to the database
        song_ids = []
        album_genre_ids = set()
        for song in album_songs:
            print(song)
            
            # Get song id
            song_id = n_songs
            n_songs += 1
            song_ids.append(song_id)
            
            # Get song duration from uniform distribution (120 - 300)
            song_duration = int(random.uniform(120, 300.01))
            
            # Get random subset of album genres 
            genres = random.sample(album_genres, k=random.randint(1, len(album_genres)))
            genre_ids = [genre_id_map[genre] for genre in genres]
            for genre_id in genre_ids: album_genre_ids.add(genre_id)

            # Add Song to database
            query = "insert into song (songid, length, title, releasedate) values ({}, {}, \'{}\', \'{}\');".format(song_id, song_duration, song, album_date)
            queries.append(query)
            db.query(query)
            
            # Add SongGenres to database
            for genre_id in genre_ids:
                query = "insert into songgenre (songid, genreid) values ({}, {});".format(song_id, genre_id)
                queries.append(query)
                db.query(query)
                
            # Add SongBys to database
            for artist_id in artist_ids:
                query = "insert into songby (songid, artistid) values ({}, {});".format(song_id, artist_id)
                queries.append(query)
                db.query(query)
                      
        # Add Album to database
        query = "insert into album (albumid, name, releasedate) values ({}, \'{}\', \'{}\');".format(album_id, album_name, album_date)
        queries.append(query)
        db.query(query)
        
        # Add AlbumContains to database
        for i in range(len(song_ids)):
            track_no = i + 1
            song_id = song_ids[i]
            query = "insert into albumcontains (albumid, songid, tracknumber) values ({}, {}, {});".format(album_id, song_id, track_no)
            queries.append(query)
            db.query(query)
        
        # Add AlbumGenre to database
        for genre_id in album_genre_ids:
            query = "insert into albumgenre (albumid, genreid) values ({}, {});".format(album_id, genre_id)
            queries.append(query)
            db.query(query)            
  
    # Write queries to text file
    print(len(queries))
    with open("queries.txt", 'w') as f:
        for query in queries:
            f.write(query + '\n')
        