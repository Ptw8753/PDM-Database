import json
from random_functions import *
from database import Database
import numpy as np
import pandas as pd
from math import *

possible_genre_combinations = [ 
    ["Rap"], ["Reggae"], ["Country"], 
    ["Pop"], ["RnB"], ["Classical"], 
    ["Electronic"], ["Rock"], ["Funk"], 
    ["Rap", "Reggae"], ["Rap", "RnB"], 
    ["Electronic", "Pop"], ["Electronic", "Funk"], 
    ["Pop", "Rock"] 
]

playlist_buzzwords = ["Awesome", "Loud", "Beats", "Music", \
    "Favorite", "Nice", "Cool", "Hard", "Fresh", \
    "Dope", "Fun", "Sound", "Hype", "Chill", "Relax", \
    "Sleep", "Outstanding", "Best", "Huge", "Dance", \
    "Good", "Songs", "Fun", "Vibes", "Disco", "Sing",
    "Mediocre", "Warm", "Coolest", "Noisy", "Greatest", \
    "Bumpin", "Real", "Ultimate", "Superior", "Heat", "Fire", \
    "Instrumental"]

if __name__ == "__main__":
    step = 4
    
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


    if step == 1:
        
        # Load attributes
        with open("songs.txt") as f: songs = [l.strip().replace("'", "") for l in f.readlines() if len(l) <= 60]
        with open("artists.txt") as f: artists = [l.strip().replace("'", "") for l in f.readlines() if len(l) <= 60]
        with open("albums.txt") as f: albums = [l.strip().replace("'", "") for l in f.readlines() if len(l) <= 60]
        with open("genres.txt") as f: genres = [l.strip() for l in f.readlines()]
        
        # Add Genre rows
        for genre_name in genres:
        
            # Get new genre id
            genre_id = n_genres
            genre_id_map[genre_name] = genre_id
            n_genres += 1
            
            # Add genre to database
            query = "insert into genre (genreid, name) values ({}, \'{}\');".format(genre_id, genre_name)
            #queries.append(query)
            db.query(query)
        
        album_songs_generator = random_subset_without_replacement(songs, min_n_album_songs, max_n_album_songs)
        album_artists_generator = random_subset_with_replacement(artists, min_n_album_artists, max_n_album_artists, size_freqs = get_inv2_frequencies(max_n_album_artists - min_n_album_artists - 1))
        for album_songs in album_songs_generator.__iter__():
            album_artists = album_artists_generator.__next__()
            album_genres = random.choice(possible_genre_combinations)
            if len(albums) == 0: raise Exception("Ran out of albums")
            album_name = random.choice(albums)
            albums.remove(album_name)
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
                    #queries.append(query)
                    db.query(query)
                    
                artist_id = artist_id_map[artist]
                artist_ids.append(artist_id)
                
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
                #queries.append(query)
                db.query(query)
                
                # Add SongGenres to database
                for genre_id in genre_ids:
                    query = "insert into songgenre (songid, genreid) values ({}, {});".format(song_id, genre_id)
                    #queries.append(query)
                    db.query(query)
                    
                # Add SongBys to database
                for artist_id in artist_ids:
                    query = "insert into songby (songid, artistid) values ({}, {});".format(song_id, artist_id)
                    #queries.append(query)
                    db.query(query)
                        
            # Add Album to database
            query = "insert into album (albumid, name, releasedate) values ({}, \'{}\', \'{}\');".format(album_id, album_name, album_date)
            #queries.append(query)
            db.query(query)
            
            # Add AlbumContains to database
            for i in range(len(song_ids)):
                track_no = i + 1
                song_id = song_ids[i]
                query = "insert into albumcontains (albumid, songid, tracknumber) values ({}, {}, {});".format(album_id, song_id, track_no)
                #queries.append(query)
                db.query(query)
            
            # Add AlbumGenre to database
            for genre_id in album_genre_ids:
                query = "insert into albumgenre (albumid, genreid) values ({}, {});".format(album_id, genre_id)
                #queries.append(query)
                db.query(query)            
                
    elif step == 2:

        n_users = 5000
        user_gen = random_user_generator()
        playlist_names_used = set()
        
        n_playlists = 0
        for user_id in range(n_users):
            print(str(user_id) + ' / ' + str(n_users))
            
            # Generate a user
            user = next(user_gen)
            user_username = user.username
            user_password = user.password
            user_firstname = user.firstName
            user_lastname = user.lastName
            user_email = user.email
            user_creation_datetime = datetime.datetime.combine(user.creationDate, datetime.datetime.min.time())
            user_lastaccess_datetime = datetime.datetime.combine(user.lastAccess, datetime.datetime.min.time())
            
            # Add user to database
            query = "insert into users (userid, username, password, firstname, lastname, email, creationdate, lastaccessdate) \
                values ({}, '{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(user_id, user.username, \
                user.password, user.firstName, user.lastName, user.email, python_datetime_to_sql(user_creation_datetime), python_datetime_to_sql(user_lastaccess_datetime))
            #queries.append(query)
            db.query(query)
            
            # Get preferred genres for user by taking the union of 1..3 sets of possible genre combinations
            rval = random.randint(1, 3)
            preferred_genres = {e for c in random.sample(possible_genre_combinations, k=rval) for e in c}
            preferred_genres = list(preferred_genres)
            
            # Get preferred songs by taking 0..50 distinct songs that have genres that are a subset of user's preferred genres
            rval = random.randint(0, 50)
            if rval == 0: continue
            preferred_genres_str = "(" + repr(preferred_genres[0]) + ")" if len(preferred_genres) == 1 else repr(tuple(preferred_genres))
            song_matches = db.query("select distinct songid, releasedate from song where (releasedate < cast('{}' as date)) and songid in \
                (select songid from songgenre where genreid in (select genreid from genre where name in {}))\
                ".format(python_date_to_sql(user_lastaccess_datetime.date()), preferred_genres_str))
            preferred_songs = random.sample(song_matches, k=rval)
            preferred_song_ids = [song[0] for song in preferred_songs]
            preferred_song_release_datetimes = [datetime.datetime.combine(song[1], datetime.datetime.min.time()) for song in preferred_songs]
            
            # Get listensto, rates for each song
            preferred_song_listen_datetimes = []
            for i in range(len(preferred_songs)):
                n_views = random.randint(1, 20)
                song_id = preferred_song_ids[i]
                song_release_datetime = preferred_song_release_datetimes[i]
                left_timestamp = datetime.datetime.timestamp(max(song_release_datetime, user_creation_datetime))
                timestamp_step = datetime.datetime.timestamp(user_lastaccess_datetime) - left_timestamp
                timestamp_step = timestamp_step / n_views
                assert timestamp_step > 0
                for j in range(n_views):
                    l = left_timestamp + (j * timestamp_step)
                    r = left_timestamp + ((j+1) * timestamp_step)
                    listen_datetime = datetime.datetime.fromtimestamp(random.uniform(l, r))
                    if j == n_views - 1:
                        preferred_song_listen_datetimes.append(listen_datetime)
                        
                    # Add listensto to database
                    query = "insert into listensto (userid, songid, listendate) \
                        values ({}, {}, '{}')".format(user_id, song_id, python_datetime_to_sql(listen_datetime))
                    #queries.append(query)
                    db.query(query)
                    
                # Add rating to database
                if random.random() < 0.5:   # Give half the songs a rating
                    rating = math.ceil(n_views / 4)
                    if rating > 5: rating = 5
                    if n_views < 4: rating = 0
                    query = "insert into rates (userid, songid, userrating) values ({}, {}, {})".format(user_id, song_id, rating)
                    #queries.append(query)
                    db.query(query)
                    
            # Get playlist, playlistcontains
            create_n_playlists = random.randint(0, math.floor(min(3, len(preferred_songs) / 20)))
            for i in range(create_n_playlists):
                n_songs = random.randint(1, 20)
                song_ids = random.sample(range(len(preferred_songs)), k=n_songs)
                while True:
                    playlist_name = "".join(random.sample(playlist_buzzwords, k=4))
                    if playlist_name not in playlist_names_used:
                        playlist_names_used.add(playlist_name)
                        break
                playlist_id = n_playlists 
                n_playlists += 1
                playlist_date = max([preferred_song_listen_datetimes[s] for s in song_ids]).date()
                
                # Add playlist to database
                query = "insert into playlist (playlistid, userid, name, creationdate) \
                    values ({}, {}, '{}', '{}')".format(playlist_id, user_id, playlist_name, python_date_to_sql(playlist_date))
                #queries.append(query)
                db.query(query)
                
                # Add playlistcontains to database
                for j in range(n_songs):
                    song_id = song_ids[j]
                    track_num = j + 1
                    query = "insert into playlistcontains (playlistid, songid, tracknumber) values ({}, {}, {})".format(playlist_id, song_id, track_num)
                    #queries.append(query)
                    db.query(query)
                    
                    
    elif step == 3:
        
        # Get the user_ids in database
        query = "select userid from users where userid < 5000 order by userid asc;"
        #queries.append(query)
        user_ids = [t[0] for t in db.query(query)]
        
        for user_id in user_ids:
            n_following = math.floor(np.random.normal(30, 15))
            if n_following <= 0: 
                continue
            print(user_id, n_following)
            follow_ids = random.sample(user_ids, k=n_following)
            for follow_id in follow_ids:
                if user_id == follow_id:
                    continue
                
                query = "insert into follows (userid, followid) values ({}, {})".format(user_id, follow_id)
                #queries.append(query)
                db.query(query)
                
    elif step == 4:
        
        query = "select artistid from artist"
        #queries.append(query)
        res = db.query(query)
        artist_ids = [a[0] for a in res]
        
        query = "select userid from users"
        #queries.append(query)
        res = db.query(query)
        user_ids = [u[0] for u in res]
        
        date = datetime.datetime(2023, 11, 16)
        for user_id in user_ids:
            query = "update users set lastaccessdate = '{}' where userid = {}".format(python_datetime_to_sql(date), user_id)
            #queries.append(query)
            db.query(query)
        
        n_groups = 200
        max = 150000
        min = 1000
        median = 12000
        Xs = np.linspace((median * median) / max, (median * median) / min, n_groups)
        Ys = np.zeros(n_groups)
        for i in range(len(Xs)):
            x = Xs[i]
            Ys[i] = floor((median * median) / x)
            
        random.shuffle(artist_ids)
        start_indices = [floor(i) for i in np.linspace(0, len(artist_ids), n_groups + 1) if i != len(artist_ids)]
        start_indices.append(len(artist_ids) - 1)

        next_start_index = 1
        seen_song_ids = set()
        for i in range(len(artist_ids)):
            
            print("Artist ({} / {})".format(i + 1, len(artist_ids)))
            
            artist_id = artist_ids[i]
            if i >= start_indices[next_start_index]:
                if next_start_index < len(start_indices) - 1:
                    next_start_index += 1
            mean_n_views = Ys[next_start_index - 1]
                    
            query = "select songid from songby where artistid = {}".format(artist_id)
            #queries.append(query)
            res = db.query(query)
            song_ids = [s[0] for s in res][:1]
            
            j = 0
            for song_id in song_ids:
                print("Song ({} / {})".format(j + 1, len(song_ids)))
                if song_id in seen_song_ids:
                    continue
                seen_song_ids.add(song_id)
                
                n_views = np.random.normal(float(mean_n_views) / 50, mean_n_views / 300)
                n_views = floor(n_views)
                if n_views <= 0: continue
                print("k = {}".format(n_views))
                
                start = pd.Timestamp('2023-11-1')
                end = pd.Timestamp('2023-11-30')
                t = np.linspace(start.value, end.value, n_views)
                t = pd.to_datetime(t)
                
                k = 0
                for user_id in random.choices(user_ids, k=n_views):
                    
                    date = t[k]
                    query = "insert into listensto (userid, songid, listendate) values ({}, {}, '{}')".format(user_id, song_id, python_datetime_to_sql(date))
                    #queries.append(query)
                    db.query(query)
                    
                    k += 1
                        
                j += 1
                
                
        
        
        
        
"""    # Write queries to text file
    print(len(queries))
    with open("queries.txt", 'w') as f:
        for query in queries:
            f.write(query + '\n')"""