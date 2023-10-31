import json
from random_functions import *
from database import Database

possible_genre_combinations = [ 
    ["Rap"], ["Reggae"], ["Country"], 
    ["Pop"], ["RnB"], ["Classical"], 
    ["Electronic"], ["Rock"], ["Funk"], 
    ["Rap", "Reggae"], ["Rap", "RnB"], 
    ["Electronic", "Pop"], ["Electronic", "Funk"], 
    ["Pop", "Rock"] 
]

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
        