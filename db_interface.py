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


    # I DONT THINK THIS ONE WILL WORK, USE search() BELOW 
    #helper function to reduce duplicate code
    def executeSongQueryWithWhereClause(self, where: str) -> str:
        query = f'''
        select song.title, artist.name, album.name, song.length, count(song.songid)
        from song
        join songby on song.songid = songby.songid
        join artist on songby.artistid = artist.artistid
        join albumcontains on song.songid = albumcontains.songid
        join album on albumcontains.albumid = album.albumid
        left join listensto on song.songid = listensto.songid
        {where}
        group by song.title, artist.name, album.name, song.length
        '''

        songData = self.database.query(query)
        albums = []
        for song in songData:
            albums.append(song[2])

        song = Song(title=songData[0][0], artistName=songData[0][1], albumNames = albums, length=songData[0][3], listenCount=songData[0][4])
        print(song)
        return song
        #populate song here


    def search(self, attribute: str, keyword: str, sort: str, sort_type: str):
        songs = dict()
        songData = self.database.query(f'''
        select song.songid, song.title, artist.name, album.name, genre.name, song.length, count(listensto.songid) as playcount
        from song
        join songby on song.songid = songby.songid
        join artist on songby.artistid = artist.artistid
        join albumcontains on song.songid = albumcontains.songid
        join album on albumcontains.albumid = album.albumid
        join songgenre on song.songid = songgenre.songid
        join genre on songgenre.genreid = genre.genreid
        left join listensto on song.songid = listensto.songid
        where {attribute} like '%{keyword}%'
        group by song.title, artist.name, album.name, genre.name, song.length, song.songid
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
            globalPlaycount = tuple[6] # TODO should this be user or global playcount?

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

        return songs.values() # return a list of song objects


    # song searches
    # each entry must list song name, artist name, album, length, and listen count
    # required
    # todo
    def searchSongByTitle(self, keyword: str, sort="song.title", sort_type="ASC"):
        return self.search("song.title", keyword, sort, sort_type)
    

    # required
    # todo
    def searchSongByArtist(self, keyword: str, sort="song.title", sort_type="ASC"):
        return self.search("artist.name", keyword, sort, sort_type)
    

    # required
    # todo
    def searchSongByAlbum(self, keyword: str, sort="song.title", sort_type="ASC"):
        return self.search("album.name", keyword, sort, sort_type)


    # required
    # todo
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
        except (select songid from playlistcontains)
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
    def deleteSongFromPlaylist(self,playlistid,songid):
        pass
        self.database.query(f'''
        delete from playlistcontains where playlistcontains.songid = {songid} 
        and playlistcontains.playlistid = {playlistid}
        ''')


    #remove intersection
    # required
    # todo
    def deleteAlbumFromPlaylist(self,playlistid,albumid):
        pass
        self.database.query(f'''
        delete from playlistcontains where albumcontains.albumid = {albumid} 
        intersect (select songid from playlistcontains))
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
        song_id = self.getSongId(song_name, user_id)

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