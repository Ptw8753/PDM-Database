import random
import sys

from database import Database
from data_classes import *
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

    #query to get all genres
    #example query
    def getAllGenres(self):
        genreData = self.database.query("select * from \"genre\"")
        genres = []
        for genre in genreData:
            genres.append(Genre(name=genre[1]))
        return genres

    #query to get all songs where length > minTime
    #example query
    def getSongByMinTimePlayed(self, minTime: str):
        songData = self.database.query(f'''
        select title, releasedate, playcount, length, genre."name" from "song"
        join "genre" on song."genreid" = genre."genreid"
        where ("length" > {minTime})
        ''')
        songs = []
        for song in songData:
            songs.append(Song(title=song[0], releaseDate=song[1], playCount=song[2], length=song[3], genre=song[4]))
        return songs

    #gets a song by name, joins artist name and genre name
    #example query
    def getSongByName(self, title: str):
        songData = self.database.query(f'''
                select title, artist."name", releasedate, playcount, length, genre."name" from "song"
                join songby on song."songid" = songby."songid"
                join artist on songby.artistid = artist."artistid"
                join genre on song."genreid" = genre."genreid"
                where (title = {title})
                ''')
        songs = []
        for song in songData:
            songs.append(Song(title=song[0], releaseDate=song[1], playCount=song[2], length=song[3], genre=song[4]))
        return songs

    #todo
    #login a user
    #checks the username and password, on successful login, update accessDateTime
    #required
    def loginUser(self, username: str, password: str):
        query = self.database.query(f'''
            select userid from users
            where (username = '{username}' and password = '{password}')
            ''')
        if(query == []):
            print("invalid username or password!")
        else:
            userId = query[0][0]
            #this query works when pasted into the datagrip console, but not here for some reason
            # could be some sort of insert/update permission issue
            self.database.query(f'''
            update users
            set lastaccessdate = '{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
            where userid = '{userId}'
            ''')

    # required
    def createPlaylist(self, userid: str, name: str):
        self.database.query(f'''
        insert into playlist(playlistid, userid, name, creationdate)
        values({self.generateIdForTable("playlist")}, {userid}, '{name}', '{datetime.now().strftime("%Y-%m-%d")}')
        ''')

    #lists the name, number of songs, and total duration
    # required
    # todo
    #lists every playlist a user has created
    # (number songs and total aren't stored explicitly
    # probably need helper function/query
    def listAllCollections(self, userid: str):
        pass
        self.database.query(f'''
        select playlist.name from playlist
        where userid = playlist.userid
        values({userid})
        ''')

    #helper function to reduce duplicate code
    def getSongJoinQuery(self) -> str:
        return ('''
        select title, artist.name, album.name, length, count
        from song
        join songby on id = songby.songid
        join artist on songby.id = artist.id
        join genre on genreid = genre.id
        #TODO GET THE PLAY COUNT
        ''')

    # song searches
    # each entry must list song name, artist name, album, length, and listen count
    # required
    # todo
    def searchSongByName(self):
        pass

    # required
    # todo
    def searchSongByArtist(self):
        pass

    # required
    # todo
    def searchSongByAlbum(self):
        pass

    # required
    # todo
    def searchSongByGenre(self):
        pass

    # required
    # todo
    def addSongToPlaylist(self):
        pass

    # required
    # todo
    def addAlbumToPlaylist(self):
        pass

    # required
    # todo
    def deleteSongFromPlaylist(self):
        pass

    #remove intersection
    # required
    # todo
    def deleteAlbumFromPlaylist(self):
        pass

    # required
    # todo
    def renamePlaylist(self):
        pass

    # required
    # todo
    def deletePlaylist(self):
        pass

    # required
    # todo
    def playSong(self):
        pass

    # required
    # todo
    def playPlaylist(self):
        pass

    # required
    #MUST BE LOGGED IN TO RUN THIS
    # todo
    def followUser(self, username: str):
        #get the user to follow
        userid = self.database.query(f"""
        select userid from users where ("username" = '{username}')
        """)[0][0]
        print(userid)

    # required
    # todo
    def unfollowUser(self):
        pass

#get next id functions create a new id greater than the max found in the database
    def generateIdForTable(self, tableName: str) -> str:
        newId = rand.randint(0, 2147483647)
        while True:
            if(self.database.query(f"""select {tableName}id from {tableName} where {tableName}id = {newId}""")) == []:
                return str(newId)
            newId = rand.randint(0, 2147483647)