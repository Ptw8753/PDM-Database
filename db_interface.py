import random
import sys

from datetime import datetime
from database import Database
from data_classes import *
from data_classes import Song
import random as rand

# this is where we should write request queries
# how to write queries:
# self.database.query(INPUT_HERE)
# this will return a value if any is given in the form [("element 1","element 2",...), ("element 1", "element 2")]
# AKA list of tuples where the tuples are rows and tuple elements are columns
# Each time we do something it should be its own function
class Interface:
    def __init__(self, username: str, password: str):
        self.database = Database(username, password)

    #login a user
    #checks the username and password, on successful login, update accessDateTime
    #required
    def loginUser(self, username: str, password: str):
        userId = None
        query = self.database.query(f'''
            select userid from users
            where (username = '{username}' and password = '{password}')
            ''')
        if(query != []):
            userId = query[0][0]
            #this query works when pasted into the datagrip console, but not here for some reason
            # could be some sort of insert/update permission issue
            self.database.query(f'''
            update users
            set lastaccessdate = '{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
            where userid = '{userId}'
            ''')
            return userId

        return userId


    # checks if a username is in the users table.
    # returns true if the username is used.
    def isUsernameUsed(self, username: str):
        query = self.database.query(f'''
            select userid from users where username = '{username}'                                  
            ''')
        return query != []


    def isPlaylistNameUsed(self, name: str):
        query = self.database.query(f'''
            select name from playlist where name = '{name}'
            ''')
        return query != []


    # converts email into userid
    # returns false if errors, true if success
    def getIDfromEmail(self, email: str):
        if not self.isEmailUsed(email):
            return False
        query = self.database.query(f'''
            select userid from users where email = '{email}'
            ''')
        if query is not None:
            return query[0][0]


    # checks if there is a user with given email
    # used for following users
    def isEmailUsed(self, email: str):
        query = self.database.query(f'''
            select userid from users where email = '{email}'
            ''')
        return query != []


    # converts email into userid
    # returns false if errors, true if success
    def getIDfromEmail(self, email: str):
        if not self.isEmailUsed(email):
            return False
        query = self.database.query(f'''
            select userid from users where email = '{email}'
            ''')
        if query is not None:
            return query[0][0]


    # create a row of user table
    # returns false if an error
    def createUser(self, username, password, firstname, lastname, email):
        id = self.generateIdForTable("users")
        d = datetime.now()
        creation_date = f"{d.year}-{d.month}-{d.day}"
        query = self.database.query(f'''
            insert into users(userid, username, password, firstname, lastname, email, creationdate, lastaccessdate)
            values({id}, '{username}', '{password}', '{firstname}', '{lastname}', '{email}', '{creation_date}', '{d}')                         
            ''')
        if self.isUsernameUsed(username):
            return True
        else:
            return False


    # required
    def createPlaylist(self, userid: str, name: str):
        self.database.query(f'''
        insert into playlist(playlistid, userid, name, creationdate)
        values({self.generateIdForTable("playlist")}, {userid}, '{name}', '{datetime.now().strftime("%Y-%m-%d")}')
        ''')


    #lists the name, number of songs, and total duration
    # required
    #lists every playlist a user has created
    # (number songs and total aren't stored explicitly
    # probably need helper function/query
    def listAllCollections(self, userid: int):
        collections = self.database.query(f'''
        select playlist.name from playlist
        where playlist.userid = {userid}
        ''')

        return collections


    def search(self, attribute: str, keyword: str, sort: str, sort_type: str):
        songs = dict()
        songData = self.database.query(f'''
        select song.songid, song.title, artist.name, album.name, genre.name, song.length, song.releasedate, count(listensto.songid) as playcount
        from song
        join songby on song.songid = songby.songid
        join artist on songby.artistid = artist.artistid
        join albumcontains on song.songid = albumcontains.songid
        join album on albumcontains.albumid = album.albumid
        join songgenre on song.songid = songgenre.songid
        join genre on songgenre.genreid = genre.genreid
        left join listensto on song.songid = listensto.songid
        where {attribute} like '%{keyword}%'
        group by song.title, artist.name, album.name, genre.name, song.length, song.releasedate, song.songid
        order by {sort} {sort_type}
        ''')
        if songData is None:
            return songs
        for tuple in songData:

            songID = tuple[0]
            songTitle = tuple[1]
            artistName = tuple[2]
            albumName = tuple[3]
            genreName = tuple[4]
            length = tuple[5]
            releaseDate = tuple[6] #useless :/
            globalPlaycount = tuple[7] # TODO should this be user or global playcount?

            if songID in songs.keys():
                s = songs.get(songID)
                if albumName not in s.albumNames:
                    s.albumNames.append(albumName)
                if genreName not in s.genres:
                    s.genres.append(genreName)
                if artistName not in s.artistNames:
                    s.artistNames.append(artistName)
                songs[songID] = s
            else:
                s = Song(title=songTitle, artistNames=[artistName], albumNames=[albumName], genres=[genreName],
                         length=length, listenCount=globalPlaycount, rating=0)
                songs[songID] = s

        return songs.values() # return a list of song objects


    # song searches
    # each entry must list song name, artist name, album, length, and listen count
    # required
    def searchSongByTitle(self, keyword: str, sort="song.title", sort_type="ASC"):
        return self.search("song.title", keyword, sort, sort_type)


    # required
    def searchSongByArtist(self, keyword: str, sort="song.title", sort_type="ASC"):
        return self.search("artist.name", keyword, sort, sort_type)


    # required
    def searchSongByAlbum(self, keyword: str, sort="song.title", sort_type="ASC"):
        return self.search("album.name", keyword, sort, sort_type)


    # required
    def searchSongByGenre(self, keyword: str, sort="song.title", sort_type="ASC"):
        return self.search("genre.name", keyword, sort, sort_type)


    def getPlaylistid(self, name, userid):
        result = self.database.query(f'''
        select playlistid from playlist where 
        playlist.name = '{name}' and
        playlist.userid = {userid}
        ''')

        if result != []:
            return result[0][0]
        else:
            return None


    def getSongId(self, name):
        songid = self.database.query(f'''
        select songid from song 
        where song.title = '{name}'
        ''')

        if(songid != []):
            return songid[0][0]
        else:
            return None


    def getAlbumId(self, name):
        albumid = self.database.query(f'''
        select albumid from album 
        where album.name = '{name}'
        ''')

        if(albumid != []):
            return albumid[0][0]
        else:
            return None


    def getAlbumSongs(self, albumid):
        songs = self.database.query(f'''
        select songid from albumcontains where albumcontains.albumid = {albumid} 
        ''')

        return songs


    def getPlaylistSongNames(self, playlistid):
        songs = self.database.query(f'''
        select title from song where songid in 
        (select songid from playlistcontains where playlistcontains.playlistid = {playlistid}) 
        ''')

        return songs


    def getPlaylistSongTotal(self, playlistid):
        songs = self.database.query(f'''
        select COUNT(songid) from playlistcontains 
        where playlistcontains.playlistid = {playlistid} 
        ''')

        return songs


    def getPlaylistDuration(self, playlistid):
        duration = self.database.query(f'''
        select SUM(length) from song where songid in
        (select songid from playlistcontains 
        where playlistcontains.playlistid = {playlistid})
        ''')

        return duration


    def getAlbumSongNames(self, albumid):
        songs = self.database.query(f'''
        select title from song where songid in (select songid from albumcontains 
        where albumcontains.albumid = {albumid})
        ''')

        return songs


    # required
    def addSongToPlaylist(self, playlistid, song_name):
        songid = self.getSongId(song_name)
        if songid == None:
            return False

        self.database.query(f'''
        insert into playlistContains values({playlistid},{songid},
        (select count(playlistid) from playlistcontains 
        where playlistcontains.playlistid = {playlistid}) + 1)
        ''')


    # required
    def addAlbumToPlaylist(self, playlistid, name):
        albumid = self.getAlbumId(name)
        if albumid == None:
            return False

        songs = self.getAlbumSongs(albumid)

        for song in songs:
            songid = song[0]

            self.database.query(f'''
            insert into playlistcontains values({playlistid}, {songid},
            (select count(playlistid) from playlistcontains 
            where playlistcontains.playlistid = {playlistid}) + 1)
            ''')


    # required
    # todo
    def deleteSongFromPlaylist(self,playlistid,name):
        songid = self.getSongId(name)

        self.database.query(f'''
        delete from playlistcontains where playlistcontains.songid = {songid} 
        and playlistcontains.playlistid = {playlistid}
        ''')


    # required
    def deleteAlbumFromPlaylist(self,playlistid,name):
        albumid = self.getAlbumId(name)

        self.database.query(f'''
        delete from playlistcontains
        where songid in ( select playlistcontains.songid
        from playlistcontains join albumcontains 
        on playlistcontains.songid = albumcontains.songid
        where albumcontains.albumid = {albumid})
        and playlistcontains.playlistid = {playlistid}
        ''')


    # required
    def renamePlaylist(self, userid: int, old_name: str, new_name: str):
        query = self.database.query(f'''
        select name from playlist where name = '{old_name}' and userid = {userid}
        ''')
        if query == []:
            return False
        else:
            self.database.query(f'''
            update playlist set name = '{new_name}'
            where name = '{old_name}' and userid = {userid}
            ''')
            return True


    # required
    def deletePlaylist(self, user_id, name):
        playlist_id = self.getPlaylistid(name, user_id)

        if playlist_id == None:
            return False

        self.clearPlaylist(playlist_id)

        self.database.query(f'''
        delete from playlist where 
        playlist.playlistid = {playlist_id} and
        playlist.userid = {user_id}
        ''')

        return True


    def clearPlaylist(self, playlist_id):
        self.database.query(f'''
        delete from playlistcontains 
        where playlistcontains.playlistid = {playlist_id}
        ''')


    def addPlayedSong(self, user_id: int, song_id: int):
        self.database.query(f'''
                insert into listensto values({user_id}, {song_id},
                '{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
                ''')


    # required
    def playSong(self, song_name, user_id):
        song_id = self.getSongId(song_name)

        if song_id == None:
            return False
        self.addPlayedSong(user_id, song_id)
        return True


    # required
    # todo
    def playPlaylist(self, user_id:int, playlist_name:str):
        #get songids for every song in the playlist
        songs = self.database.query(f'''
            select songid from playlistcontains
            join playlist on playlistcontains.playlistid = playlist.playlistid
            where playlist.name = '{playlist_name}' ''')
        for song in songs:
            self.addPlayedSong(user_id, song[0])


    # returns true if user w/ id is following user with otherid
    def isFollowing(self, id: int, otherid: int):
        query = self.database.query(f'''
            select userid from follows where userid = {id} and followid = {otherid}
            ''')
        if query == []:
            return False
        else:
            return True


    # follow another user by giving their email
    # return success T/F
    def followUserEmail(self, userid: int, emailtofollow: str):
        otherid = self.getIDfromEmail(emailtofollow)
        if otherid is None:
            return False
        query = self.database.query(f'''
            insert into follows(userid, followid)
            values('{userid}', '{otherid}')
            ''')
        return self.isFollowing(userid, otherid)


    # unfollow a user by giving their email
    # return success T/F
    def unfollowUserEmail(self, userid: int, emailtounfollow: str):
        otherid = self.getIDfromEmail(emailtounfollow)
        if otherid is None:
            return False
        query = self.database.query(f'''
            delete from follows
            where userid = {userid} and followid = {otherid}
            ''')
        return not self.isFollowing(userid, otherid)


    def getTop50Rolling(self):
        return self.top50SongMapping('''
        select genre.name, limitedResult.* from genre
        join songgenre on genre.genreid = songgenre.genreid
        join (select song.songid, song.title, artist.name, album.name, song.length, song.releasedate, subquery.numRatings as playcount
        from song
        join songby on song.songid = songby.songid
        join artist on songby.artistid = artist.artistid
        join albumcontains on song.songid = albumcontains.songid
        join album on albumcontains.albumid = album.albumid
        join songgenre on song.songid = songgenre.songid
        join genre on songgenre.genreid = genre.genreid
        JOIN rates ON song.songid = rates.songid
        JOIN listensto ON song.songid = listensto.songid
        JOIN (SELECT songid, COUNT(songid) AS numRatings
        FROM listensto
        WHERE listendate > CURRENT_DATE - INTERVAL '30 days'
        GROUP BY songid) AS subquery ON song.songid = subquery.songid
        WHERE listendate > CURRENT_DATE - INTERVAL '30 days'
        GROUP BY song.songid, song.title, artist.name, album.name, song.length, song.releasedate, song.songid, subquery.numRatings
        ORDER BY numRatings DESC
        LIMIT 50) as limitedResult on limitedResult.songid = songgenre.songid
        order by playcount desc
        ''')

    def getTop50AmongFollowers(self, userid: int):
        return self.top50SongMapping(f'''
        select genre.name, limitedResult.* from genre
        join songgenre on genre.genreid = songgenre.genreid
        join (select song.songid, song.title, artist.name, album.name, song.length, song.releasedate, subquery.numRatings as playcount
        from song
        join songby on song.songid = songby.songid
        join artist on songby.artistid = artist.artistid
        join albumcontains on song.songid = albumcontains.songid
        join album on albumcontains.albumid = album.albumid
        join songgenre on song.songid = songgenre.songid
        join genre on songgenre.genreid = genre.genreid
        JOIN rates ON song.songid = rates.songid
        JOIN listensto ON song.songid = listensto.songid
        JOIN (SELECT songid, COUNT(songid) AS numRatings
        FROM (select * from listensto
        where userid in (select follows.userid from follows where followid = {userid})) as followerListens
        GROUP BY songid) AS subquery ON song.songid = subquery.songid
        GROUP BY song.songid, song.title, artist.name, album.name, song.length, song.releasedate, song.songid, subquery.numRatings
        ORDER BY numRatings DESC
        LIMIT 50) as limitedResult on limitedResult.songid = songgenre.songid
        ORDER BY limitedResult.playcount DESC
        ''')

    def top50SongMapping(self, queryString: str):
        songData = self.database.query(queryString)
        songs = dict()
        if songData is None:
            return songs
        for tuple in songData:
            genreName = tuple[0]
            songID = tuple[1]
            songTitle = tuple[2]
            artistName = tuple[3]
            albumName = tuple[4]
            length = tuple[5]
            releaseDate = tuple[6]  # useless :/
            globalPlaycount = tuple[7]  # TODO should this be user or global playcount?
            if songID in songs.keys():
                s = songs.get(songID)
                if albumName not in s.albumNames:
                    s.albumNames.append(albumName)
                if genreName not in s.genres:
                    s.genres.append(genreName)
                if artistName not in s.artistNames:
                    s.artistNames.append(artistName)
                songs[songID] = s
            else:
                s = Song(songTitle, [artistName], [albumName], [genreName], length, globalPlaycount)
                songs[songID] = s
        return list(songs.values())  # return a list of song objects

    def getTop5Genres(self):
        genres = self.database.query('''
        select genre.name, count(listensto) as numPlays
        from genre
        join songgenre on genre.genreid = songgenre.genreid
        join listensto on songgenre.songid = listensto.songid
        where listendate >= date_trunc('month', current_date)
        and listendate < date_trunc('month', current_date) + interval '1 month'
        group by genre.name
        order by numPlays desc
        limit 5
        ''')
        topGenres = []
        for tuple in genres:
            topGenres.append(TopGenre(genreName=tuple[0], listenCount=tuple[1]))
        return topGenres

    def recommendSongs(self, user_id):
        top_10_from_followers = self.top50SongMapping(f'''
        select genre.name, songQuery.songid, title, artist.name, album.name, song.length, song.releasedate, songQuery.count
        from (select songid, count(songid) as count
        from(select userid, songid from listensto where songid in (select songid from listensto
        except
        select songid from listensto
        where userid = {user_id})) as listenExclusive
        join follows on listenExclusive.userid = follows.userid
        where followid = {user_id}
        group by songid
        order by count desc) as songQuery
        join song on song.songid = songQuery.songid
        join songGenre on songgenre.songid = songQuery.songid
        join genre on genre.genreid = songGenre.genreid
        join songby on songby.songid = songQuery.songid
        join artist on artist.artistid = songby.artistid
        join albumcontains on albumcontains.songid = songQuery.songid
        join album on album.albumid = albumcontains.albumid
        order by count desc
        limit 10
        ''')

        top_10_from_artists = self.top50SongMapping(f'''select genre.name, songQuery.songid, title, artist.name, album.name, song.length, song.releasedate, songQuery.count
        from (select listenExclusive.songid, count(listenExclusive.songid) as count
        from(select userid, songid from listensto where songid in (select songid from listensto
        except
        select songid from listensto
        where userid = {user_id})) as listenExclusive
        join songby on songby.songid = listenExclusive.songid
        where artistid in
        (select artist.artistid from listensto
        join users on listensto.userid = users.userid
        join song on listensto.songid = song.songid
        join songby on song.songid = songby.songid
        join artist on songby.artistid = artist.artistid
        where users.userid = {user_id}
        group by artist.artistid
        order by count(artist.name) DESC
        LIMIT 10)
        group by listenExclusive.songid
        order by count desc) as songQuery
        join song on song.songid = songQuery.songid
        join songGenre on songgenre.songid = songQuery.songid
        join genre on genre.genreid = songGenre.genreid
        join songby on songby.songid = songQuery.songid
        join artist on artist.artistid = songby.artistid
        join albumcontains on albumcontains.songid = songQuery.songid
        join album on album.albumid = albumcontains.albumid
        order by count desc
        limit 10''')

        result = []
        result += top_10_from_followers
        result += top_10_from_artists
        return result

    def top10ArtistForUser(self, user: int):
        return self.database.query(f'''select artist.name from listensto
        join users on listensto.userid = users.userid
        join song on listensto.songid = song.songid
        join songby on song.songid = songby.songid
        join artist on songby.artistid = artist.artistid
        where users.userid = {user}
        group by artist.name
        order by count(artist.name) DESC
        LIMIT 10''')

    def rateSong(self, user_id: int, song_to_rate: str, rating: int):
        # check that rating is between 1 and 5
        if rating not in [1,2,3,4,5]:
            return False

        #get the song id to rate
        song_id = self.database.query(f'''select songid from song where title = '{song_to_rate}' ''')[0][0]

        #check for existing rating
        if self.isExistingRating(user_id, song_id):
            #update existing rating
            self.database.query(f'''
                        update rates set userrating = '{rating}'
                        where userid = '{user_id}' and songid = {song_id}
                        ''')
            return True
        else:
            #add new rating
            self.database.query(f'''
                        insert into rates(userid, songid, userrating)
                        values({user_id}, '{song_id}', '{rating}')  
                        ''')
            return True


    def isExistingRating(self, user_id: int, song_id: int):
        return not self.database.query(f'''select * from rates where userid = {user_id} and songid = {song_id} ''') == []


    def getCollectionCount(self, user_id):
        count = self.database.query(f'''
        select count(playlistid) from playlist where
        playlist.userid = {user_id}
        ''')

        return count[0][0]


    def getFollowerCount(self, user_id):
        count = self.database.query(f'''
        select count(followid) from follows where
        follows.followid = {user_id}
        ''')

        return count[0][0]


    def getFollowingCount(self, user_id):
        count = self.database.query(f'''
        select count(userid) from follows where
        follows.userid = {user_id}
        ''')

        return count[0][0]


    #get next id functions create a new id greater than the max found in the database
    def generateIdForTable(self, tableName: str) -> str:
        newId = rand.randint(0, 2147483647)
        while True:
            id = f"{tableName}id"
            if tableName == "users":
                id = "userid"
            if(self.database.query(f"""select {id} from {tableName} where {id} = {newId}""")) == []:
                return str(newId)
            newId = rand.randint(0, 2147483647)