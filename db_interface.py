from database import Database
from data_classes import *


# this is where we should write request queries
# how to write queries:
# self.database.query(INPUT_HERE)
# this will return a value if any is given in the form [("element 1","element 2",...), ("element 1", "element 2")]
# AKA list of tuples where the tuples are columns
# Each time we do something it should be its own function
class Interface:
    def __init__(self, username: str, password: str):
        self.database = Database(username, password)

    #query to get all genres
    def getAllGenres(self):
        genreData = self.database.query("select * from \"genre\"")
        genres = []
        for genre in genreData:
            genres.append(Genre(name=genre[1]))
        return genres

    #query to get all songs where length > minTime
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