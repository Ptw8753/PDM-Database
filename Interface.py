from database import Database
from data_classes import *


# this is where we should write request queries
class Interface:
    def __init__(self, username: str, password: str):
        self.database = Database(username, password)


    def getAllGenres(self):
        genreData = self.database.query("select * from \"genre\"")
        genres = []
        for genre in genreData:
            genres.append(Genre(name=genre[1]))
        return genres


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

    #login a user
    #checks the username and password, on successful login, update accessDateTime
    def loginUser(self, username: str, password: str):
        query = self.database.query(f'''
            select userid from users
            where (username = '{username}' and password = '{password}')
            ''')
        if(query == []):
            print("invalid username or password!")
        else:
            #should be the only thing returned
            userId = query[0][0]
            #this might not work
            self.database.query(f'''
            update users
            set lastaccessdate = '{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
            where userid = '{userId}'
            ''')