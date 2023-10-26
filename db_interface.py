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
        songData = self.database.query('''
        select title, releasedate, playcount, length, genre."name" from "song"
        join "genre" on song."genreid" = genre."genreid"
        where ("length" > {length})
        '''.format(length=minTime))
        songs = []
        for song in songData:
            songs.append(Song(title=song[0], releaseDate=song[1], playCount=song[2], length=song[3], genre=song[4]))
        return songs

    def getSongByName(self, title: str):
        songData = self.database.query('''
                select title, artist."name", releasedate, playcount, length, genre."name" from "song"
                join songby on song."songid" = songby."songid"
                join artist on songby.artistid = artist."artistid"
                join genre on song."genreid" = genre."genreid"
                where (title = {title})
                '''.format(title=title))
        songs = []
        for song in songData:
            songs.append(Song(title=song[0], releaseDate=song[1], playCount=song[2], length=song[3], genre=song[4]))
        return songs