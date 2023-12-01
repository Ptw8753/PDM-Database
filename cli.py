from db_interface import Interface

# if this breaks for you, do "python -m pip install rich"
from rich.console import Console
from rich.markdown import Markdown
from rich.columns import Columns
from rich.panel import Panel

class Cli:
    def __init__(self, interface: Interface):
        self.interface = interface
        self.console = Console()
        self.screen = "main"
        self.login_id = None

        self.console.clear()
        self.render_heading()
        self.input_loop()


    def print_options(self):
        if self.screen == "main":
            column1 ="""[bright_green]
* login \[username] \[password]  
* signup  
* listen \[songname] or \[albumname]  
"""
            column2 ="""[bright_green]
* rate \[songname] \[rating (1-5)]   
* follow \[useremail]  
* unfollow \[useremail]  
"""
            column3 ="""[bright_green]
* statistics
* collections  
* search
"""

        elif self.screen == "collections":
            column1 ="""[bright_red]
* create \[name]  
* +album \[collectionname]  
* +song \[collectionname]  
* rename \[name] \[newname]  
"""

            column2 ="""[bright_red]
* delete \[name]  
* -album \[collectionname]  
* -song \[collectionname]  
* listen \[collectionname]  
"""

        elif self.screen == "search":
            column1 ="""[bright_blue]
* songs \[songname]
* albums \[albumname]
* artists \[artistname]
* genres \[genre]
"""
            column2 =""""""

        elif self.screen == "statistics":
            column1 ="""[bright_yellow]
* globalrankings
* followerrankings
* topgenres 
* recommendations
* topartists
"""

            column2 =""""""
        
        if self.screen == "collections":
            self.console.print(Columns(
                    [Panel(Columns([column1, column2]), title="Command List"), 
                    Panel(Columns(self.render_collections()), title="Collections")]))
        elif self.screen == "statistics":
            self.console.print(Columns(
                    [Panel(Columns([column1, column2]), title="Command List"), 
                    Panel(Columns(self.render_statistics()), title="User Stats")]))
        elif self.screen == "main":
            self.console.print(Panel(Columns([column1, column2, column3]), title="Command List"))
        else:
            self.console.print(Panel(Columns([column1, column2]), title="Command List"))
            
    
    def render_heading(self):
        header = """# Principles of Data Management: Music Domain
Enter "quit" or "q" to """

        if self.screen in ["collections", "search", "statistics"]:
            end = """return."""
        else:
            end = """exit."""

        self.console.print(Markdown(header + end))
        if self.screen == "search":
            self.console.print()
            self.console.print("Search in:")

    
    def stringify(self, lst):
        str = ""
        for word in lst:
            str += (" " + word)

        return str[1:]
    

    def render_collections(self):
        columns = []
        column = "[bright_red]"
        line_start = "* "

        if self.login_id == None:
            return ["Log in to see collections."]
        else:
            collections = self.interface.listAllCollections(self.login_id)

            if collections is None:
                return ["You have no collections."]
            else:
                collections.sort()

        i = 0
        for collection in collections:
            column += "\n" + line_start + collection[0] + "  "
            playlistid = self.interface.getPlaylistid(collection[0], self.login_id)
            total_songs = self.interface.getPlaylistSongTotal(playlistid)[0][0]
            
            duration = self.interface.getPlaylistDuration(playlistid)[0][0]
            if duration == None:
                duration = 0
            mins = str(duration // 60) + "min "
            seconds = str(duration % 60) + "sec  "

            column += "\n|-> Total songs: " + str(total_songs) + "  "
            column += "\n|-> Duration: " + mins + seconds + "\n"
            i += 1

            if i % 4 == 0:
                column += "\n"
                columns.append(column)
                column = "[bright_red]"

        columns.append(column)
        return columns


    def render_statistics(self):
        if self.login_id == None:
            return ["Log in to see user statistics."]

        columns = []
        column = "\n[bright_yellow]  Total collections: "
        column += (str(self.interface.getCollectionCount(self.login_id)))
        column += "\n[bright_yellow]  Total followers: "
        column += (str(self.interface.getFollowerCount(self.login_id)))
        column += "\n[bright_yellow]  Total following: "
        column += (str(self.interface.getFollowingCount(self.login_id)) + "\n")

        columns.append(column)
        return columns


    def login(self, command):
        if len(command) != 3:
            self.console.print("Invalid arguments, usage: login \[username] \[password]") 
            self.console.input("Press enter to continue...")
        else:
            user = self.interface.loginUser(command[1], command[2])
            if user == self.login_id or user == None:
                self.console.print("Invalid username or password.")
                self.console.input("Press enter to continue...")
            else:
                self.login_id = user
                self.console.print("Successfully logged in as user " + command[1])
                self.console.input("Press enter to continue...")
                

    def signup(self, command):
        username = self.console.input("Username: ")
        x = self.interface.isUsernameUsed(username)
        while (x):
            self.console.print("That username is already taken!")
            username = self.console.input("Username: ")
            x = self.interface.isUsernameUsed(username)

        password = self.console.input("Password: ")
        y = len(password) < 8
        while(y):
            self.console.print("Your password must be at least 8 characters long!")
            password = self.console.input("Password: ")
            y = len(password) < 8
        fname = self.console.input("First Name: ")
        lname = self.console.input("Last Name: ")
        email = self.console.input("Email: ")
        z = self.interface.isEmailUsed(email)
        while (z):
            self.console.print("That email is already associated with an account!")
            email = self.console.input("Email: ")
            z = self.interface.isEmailUsed(email)
        success = self.interface.createUser(username, password, fname, lname, email)
        if success:
            self.console.print(f"Account successfully created!\nWelcome {fname} {lname}")
        else:
            self.console.print("Something went wrong! Account was not created :(")
        self.console.input("Press enter to continue...")


    def listen(self, command):
        title = self.stringify(command[1:])

        if len(command) < 2:
            self.console.print("Invalid arguments, usage: \nlisten \[songname]\nlisten \[albumname]")
            self.console.input("Press enter to continue...")
        else:
            result = self.interface.getAlbumId(title)
            if result != None:
                songs = self.interface.getAlbumSongNames(result)
                for song in songs:
                    title = song[0]
                    self.interface.playSong(title, self.login_id)
                    self.console.print("Now playing: " + title)
            else:
                result = self.interface.playSong(title, self.login_id)
                if result == False:
                    self.console.print("Song does not exist.")
                else:
                    self.console.print("Now playing: " + title)
            self.console.input("Press enter to continue...")


    def follow(self, command):
        if self.login_id is None:
            self.console.print("You must be logged in!")
            self.console.input("Press enter to continue...")
            return
        if len(command) == 1:
            self.console.print("Invalid arguments, usage: follow \[email]") 
            self.console.input("Press enter to continue...")
            return
        email = command[1]
        x = self.interface.isEmailUsed(email)
        while not x:
            self.console.print(f"Unable to find user: {email} ... Try again")
            email = self.console.input("Enter email of user you want to follow: ")
            x = self.interface.isEmailUsed(email)
        
        if self.interface.isFollowing(self.login_id, self.interface.getIDfromEmail(email)):
            self.console.print("You are already following that user!")
            self.console.input("Press enter to continue...")
            return
        success = self.interface.followUserEmail(self.login_id, email)
        if success:
            self.console.print(f"Successfully followed user {email}")
            self.console.input("Press enter to continue...")
        else:
            self.console.print("Something went wrong")
            self.console.input("Press enter to continue...")


    def unfollow(self, command):
        if self.login_id is None:
            self.console.print("You must be logged in!")
            self.console.input("Press enter to continue...")
            return
        if len(command) == 1:
            self.console.print("Invalid arguments, usage: follow \[email]") 
            self.console.input("Press enter to continue...")
            return
        email = command[1]
        x = self.interface.isEmailUsed(email)
        while not x:
            self.console.print(f"Unable to find user: {email} ... Try again")
            email = self.console.input("Enter email of user you want to follow: ")
            x = self.interface.isEmailUsed(email)
        if not self.interface.isFollowing(self.login_id, self.interface.getIDfromEmail(email)):
            self.console.print("You are not following that user!")
            self.console.input("Press enter to continue...")
            return
        success = self.interface.unfollowUserEmail(self.login_id, email)
        if success:
            self.console.print(f"Successfully unfollowed user {email}")
            self.console.input("Press enter to continue...")
        else:
            self.console.print("Something went wrong")
            self.console.input("Press enter to continue...") 


    def create(self, command):
        name = self.stringify(command[1:])

        if (self.login_id == None):
            self.console.print("Log in to create a collection.")
            self.console.input("Press enter to continue...")
            return

        if len(command) < 2:
            self.console.print("Invalid arguments, usage: create \[name]")
            self.console.input("Press enter to continue...")
        else:
            self.interface.createPlaylist(self.login_id, name)
            self.console.print(f"Successfully created {name}.")
            self.console.input("Press enter to continue...")


    def delete(self, command):
        if len(command) < 2:
            self.console.print("Invalid arguments, usage: create \[name]")
            self.console.input("Press enter to continue...")

        name = self.stringify(command[1:])

        if (self.login_id == None):
            self.console.print("Log in to delete a collection.")
            self.console.input("Press enter to continue...")
            return
        if self.interface.listAllCollections(self.login_id) == []:
            self.console.print("You have no collections to delete.")
            self.console.input("Press enter to continue...")
            return
        else:
            result = self.interface.deletePlaylist(self.login_id, name)
            if result == False:
                self.console.print(f"Collection {name} does not exist.")
            else:
                self.console.print(f"Successfully deleted {name}.")
            self.console.input("Press enter to continue...")


    def add_album(self, command):
        if len(command) < 2:
            self.console.print("Invalid arguments, usage: +album \[collectionname]")
            self.console.input("Press enter to continue...")
        
        name = self.stringify(command[1:])

        if (self.login_id == None):
            self.console.print("Log in to add an album's songs to a collection.")
            self.console.input("Press enter to continue...")
            return
        if self.interface.getPlaylistid(name, self.login_id) == []:
            self.console.print("You have no collections to add songs to.")
            self.console.input("Press enter to continue...")
            return
        else:
            playlistid = self.interface.getPlaylistid(name, self.login_id)
            if playlistid == None:
                self.console.print(f"Collection {name} does not exist.")
            else:
                album = self.console.input("Add album: ")
                result = self.interface.addAlbumToPlaylist(playlistid, album)
                if result == False:
                    self.console.print("Invalid album.")
                else:
                    self.console.print(f"Successfully added album {album} to collection.")
                self.console.input("Press enter to continue...")
                return
              

    def delete_album(self, command):
        if len(command) < 2:
            self.console.print("Invalid arguments, usage: -album \[collectionname]")
            self.console.input("Press enter to continue...")
        
        name = self.stringify(command[1:])

        if (self.login_id == None):
            self.console.print("Log in to delete album's songs from a collection.")
            self.console.input("Press enter to continue...")
            return
        if self.interface.getPlaylistid(name, self.login_id) == []:
            self.console.print("You have no collections to delete songs from.")
            self.console.input("Press enter to continue...")
            return
        else:
            playlistid = self.interface.getPlaylistid(name, self.login_id)
            if playlistid == None:
                self.console.print(f"Collection {name} does not exist.")
            else:
                album = self.console.input("Delete album: ")
                result = self.interface.deleteAlbumFromPlaylist(playlistid, album)
                if result == False:
                    self.console.print("Invalid album.")
                else:
                    self.console.print(f"Successfully deleted album {album} from collection.")
                self.console.input("Press enter to continue...")
                return


    def add_song(self, command):
        if len(command) != 2:
            self.console.print("Invalid arguments, usage: +song \[collectionname]")
            self.console.input("Press enter to continue...")
            return

        name = self.stringify(command[1:])

        if (self.login_id == None):
            self.console.print("Log in to add songs to a collection.")
            self.console.input("Press enter to continue...")
            return
        if self.interface.getPlaylistid(name, self.login_id) == []:
            self.console.print("You have no collections to add songs to.")
            self.console.input("Press enter to continue...")
            return
        else:
            playlistid = self.interface.getPlaylistid(name, self.login_id)
            if playlistid == None:
                self.console.print(f"Collection {name} does not exist.")
            else:
                self.console.print("Enter \"quit\" or \"q\" to stop.")
                song = self.console.input("Add song: ")
                while song not in ["q", "quit"]:
                    result = self.interface.addSongToPlaylist(playlistid, song)
                    if result == False:
                        self.console.print("Invalid song.")
                    song = self.console.input("Add song: ")

                self.console.print(f"Successfully added songs to collection.")
            self.console.input("Press enter to continue...")


    def delete_song(self, command):
        if len(command) < 2:
            self.console.print("Invalid arguments, usage: -song \[collectionname]")
            self.console.input("Press enter to continue...")
        
        name = self.stringify(command[1:])

        if (self.login_id == None):
            self.console.print("Log in to delete album's songs from a collection.")
            self.console.input("Press enter to continue...")
            return
        if self.interface.getPlaylistid(name, self.login_id) == []:
            self.console.print("You have no collections to delete songs from.")
            self.console.input("Press enter to continue...")
            return
        else:
            playlistid = self.interface.getPlaylistid(name, self.login_id)
            if playlistid == None:
                self.console.print(f"Collection {name} does not exist.")
            else:
                song = self.console.input("Delete song: ")
                result = self.interface.deleteSongFromPlaylist(playlistid, song)
                if result == False:
                    self.console.print("Invalid song.")
                else:
                    self.console.print(f"Successfully deleted song {song} from collection.")
                self.console.input("Press enter to continue...")
                return


    def edit_name(self, command):
        if self.login_id is None:
            self.console.print("You must be logged in!")
            self.console.input("Press enter to continue...")
            return
        if len(command) != 3:
            self.console.print("Invalid arguments, usage: rename \[playlist] \[new name]") 
            self.console.input("Press enter to continue...")
            return
        success = self.interface.renamePlaylist(self.login_id, command[1], command[2])
        if not success:
            self.console.print(f"Cannot find playlist: '{command[1]}'")
            self.console.input("Press enter to continue...")

    
    def listen_collection(self, command):
        title = self.stringify(command[1:])

        if len(command) < 2:
            self.console.print("Invalid arguments, usage: \nlisten \[collectionname]")
            self.console.input("Press enter to continue...")
        else:
            result = self.interface.getPlaylistid(title, self.login_id)
            if result != None:
                songs = self.interface.getPlaylistSongNames(result)
                for song in songs:
                    title = song[0]
                    self.interface.playSong(title, self.login_id)
                    self.console.print("Now playing: " + title)
            else:
                self.console.print("Song does not exist.")

            self.console.input("Press enter to continue...")


    # search command goes as follows
    # seach <subject> <keyword> optional=<order by>
    # helper function to print list of songs page by page w/ specified songsPerPage (default 15)
    def nice_print(self, songList, keyword, songsPerPage=15):
        numSongs = len(songList)

        if keyword != None:
            self.console.print(f"Search Complete!\n{len(songList)} songs found with keyword: '{keyword}'")
        
        self.console.input("Press enter to view results...")
        self.console.clear()

        n = 0
        currentPage = 0
        if songsPerPage != 0:
            maxPage = int(numSongs / songsPerPage) + 1
            if numSongs % songsPerPage == 0:
                maxPage -= 1
        for song in songList:
            n += 1
            artists = ""
            for artist in song.artistNames:
                artists += (f"[bright_blue]{artist}[white], ")
            albums = ""
            for album in song.albumNames:
                albums += (f"[bright_red]{album}[white], ")
            genres = ""
            for genre in song.genres:
                genres += (genre + ", ")
            self.console.print(f"{n}: [bright_green]{song.title} [white]by {artists[:-2]} \n\t[white]Appears on:\t{albums[:-2]} \n\t[white]Genres:\t\t{genres[:-2]} \n\tPlaycount:\t{song.listenCount}")
            if (songsPerPage != 0) and (n % songsPerPage == 0):
                currentPage += 1
                quit = self.console.input(f"------------------------------------------ Page {currentPage} of {maxPage}\nPress Enter to view next page...\nEnter 'q' or 'quit' to exit search results")
                if quit in ['q', 'quit', 'Q', 'Quit', 'QUIT']:
                    self.console.clear()
                    return
                self.console.clear()

        if currentPage > 0 and currentPage != maxPage:
            currentPage += 1
            self.console.input(f"------------------------------------------ Page {currentPage} of {maxPage}\nPress enter to close search results...")
        else:
            self.console.input("------------------------------------------\nPress enter to close search results...")


    def invalid_search(self):
        self.console.print("Invalid arguments, usage: songs \[keyword] (optional=\[sort by] optional=\[ASC/DESC]) optional=\[songs per page (0 = print all)]")
        self.console.input("Press enter to continue...")


    def get_search_args(self, command):
        keyword = None
        sort_attribute = None
        sort_order = None
        songs_per_page = None
        x = len(command)
        if x not in [2, 3, 4, 5]:
            self.invalid_search()
            return
        keyword = command[1] # if x is at least 2
        if x in [3, 5]:        # if x is 3 or 5
            songs_per_page = command[x-1]
        if x in [4, 5]:              # if x is 4 or 5
            sort_attribute = command[2]
            sort_order = command[3]
        return (keyword, sort_attribute, sort_order, songs_per_page)


    def search_songs(self, command):
        if len(command) >= 2:
            if command[1] is None:
                self.invalid_search()
                return
        keyword, sort_attribute, sort_order, songs_per_page = self.get_search_args(command)
        if sort_attribute is None and sort_order is None:
            self.console.print("Searching...")
            songList = self.interface.searchSongByTitle(keyword)
        elif sort_attribute is not None and sort_order is not None:
            self.console.print("Searching...")
            songList = self.interface.searchSongByTitle(keyword, sort_attribute, sort_order)
        else:
            self.invalid_search()
            return
        if songs_per_page is not None:
            self.nice_print(songList, keyword, int(songs_per_page))
        else:
            self.nice_print(songList, keyword)
        

    def search_albums(self, command):
        keyword, sort_attribute, sort_order, songs_per_page = self.get_search_args(command)
        if sort_attribute is None and sort_order is None:
            self.console.print("Searching...")
            songList = self.interface.searchSongByAlbum(keyword)
        elif sort_attribute is not None and sort_order is not None:
            self.console.print("Searching...")
            songList = self.interface.searchSongByAlbum(keyword, sort_attribute, sort_order)
        else:
            self.invalid_search()
            return
        if songs_per_page is not None:
            self.nice_print(songList, keyword, int(songs_per_page))
        else:
            self.nice_print(songList, keyword)


    def search_artists(self, command):
        keyword, sort_attribute, sort_order, songs_per_page = self.get_search_args(command)
        if sort_attribute is None and sort_order is None:
            self.console.print("Searching...")
            songList = self.interface.searchSongByArtist(keyword)
        elif sort_attribute is not None and sort_order is not None:
            self.console.print("Searching...")
            songList = self.interface.searchSongByArtist(keyword, sort_attribute, sort_order)
        else:
            self.invalid_search()
            return
        if songs_per_page is not None:
            self.nice_print(songList, keyword, int(songs_per_page))
        else:
            self.nice_print(songList, keyword)


    def search_genres(self, command):
        keyword, sort_attribute, sort_order, songs_per_page = self.get_search_args(command)
        if sort_attribute is None and sort_order is None:
            self.console.print("Searching...")
            songList = self.interface.searchSongByGenre(keyword)
        elif sort_attribute is not None and sort_order is not None:
            self.console.print("Searching...")
            songList = self.interface.searchSongByGenre(keyword, sort_attribute, sort_order)
        else:
            self.invalid_search()
            return
        if songs_per_page is not None:
            self.nice_print(songList, keyword, int(songs_per_page))
        else:
            self.nice_print(songList, keyword)


    def rate(self, command):
        if self.login_id is None:
            self.console.print("You must be logged in!")
            self.console.input("Press enter to continue...")
            return
        if len(command) != 3:
            self.console.print("Invalid arguments, usage: rate \[song name] \[rating]")
            self.console.input("Press enter to continue...")
            return
        rating = command[2]
        song = command[1].replace('_', ' ')
        if not rating.isdigit():
            self.console.print("Invalid argument: rating should be an integer 0-5")
            self.console.input("Press enter to continue...")
            return
        if int(rating) < 0 or int(rating) > 5:
            self.console.print("Invalid argument: rating should be an integer 0-5")
            self.console.input("Press enter to continue...")
            return
        success = self.interface.rateSong(self.login_id, song, int(rating))
        if success:
            self.console.print(f"Rated {song}: {rating}")
            self.console.input("Press enter to continue...")
        else:
            self.console.input(f"Unable to find song: {song}\nPress enter to continue...")


    def global_songs(self, command):
        songs = self.interface.getTop50Rolling()
        self.nice_print(songs, None, 10)


    def follower_songs(self, command):
        if self.login_id == None:
            self.console.print("Log in to see the top songs from your followers.") 
            self.console.input("Press enter to continue...")
        else:
            songs = self.interface.getTop50AmongFollowers(self.login_id)
            self.nice_print(songs, None, 10)


    def genre_rankings(self, command):
        genres = self.interface.getTop5Genres()
        i = 1
        print("Top genres in the past month:")
        for genre in genres:
            print(str(i) + ". " + str(genre.genreName))
            print("   Total plays: " + str(genre.listenCount) + "\n")
            i += 1
        self.console.input("Press enter to continue...")


    def recommend(self, command):
        if self.login_id == None:
            self.console.print("Log in to see the recommended songs from similar users.") 
            self.console.input("Press enter to continue...")
        else:
            songs = self.interface.recommendSongs(self.login_id)
            self.console.print("Bulding a list of songs based on your most played songs...")
            self.nice_print(songs, None, 10)

    
    def topartists(self, command):
        if self.login_id == None:
            self.console.print("Log in to see your top artists.") 
            self.console.input("Press enter to continue...")
        else:
            artists = self.interface.top10ArtistForUser(self.login_id)
            i = 1
            print("Your top artists:")
            for artist in artists:
                print(str(i) + ".\t" + str(artist[0]))
                i += 1
            self.console.input("Press enter to continue...")


    def input_loop(self):
        input_str = "null"

        while(True):
            self.print_options()
            input_str = self.console.input("> ")
            
            command = input_str.split()
            if (not command):
                self.console.clear()
                self.render_heading()
                continue

            if (self.screen == "main"):
                if (command[0] == "login"):
                    self.login(command)

                elif (command[0] == "signup"):
                    self.signup(command)
                
                elif (command[0] == "collections"):
                    self.screen = "collections"

                elif (command[0] == "search"):
                    self.screen = "search"

                elif (command[0] == "listen"):
                    self.listen(command)

                elif (command[0] == "rate"):
                    self.rate(command)

                elif (command[0] == "follow"):
                    self.follow(command)
                
                elif (command[0] == "unfollow"):
                    self.unfollow(command)

                elif (command[0] in ["statistics", "stats"]):
                    self.screen = "statistics"
            
            elif (self.screen == "collections"):
                if (command[0] == "create"):
                    self.create(command)
                
                elif (command[0] == "delete"):
                    self.delete(command)

                elif (command[0] == "+album"):
                    self.add_album(command)

                elif (command[0] == "-album"):
                    self.delete_album(command)

                elif (command[0] == "+song"):
                    self.add_song(command)

                elif (command[0] == "-song"):
                    self.delete_song(command)

                elif (command[0] == "rename"):
                    self.edit_name(command)

                elif (command[0] == "listen"):
                    self.listen_collection(command)

            elif (self.screen == "search"):
                if (command[0] == "songs"):
                    self.search_songs(command)
                
                elif (command[0] == "albums"):
                    self.search_albums(command)

                elif (command[0] == "artists"):
                    self.search_artists(command)

                elif (command[0] == "genres"):
                    self.search_genres(command)

            elif (self.screen == "statistics"):
                if (command[0] == "globalrankings"):
                    self.global_songs(command)
                elif (command[0] == "followerrankings"):
                    self.follower_songs(command)
                elif (command[0] == "topgenres"):
                    self.genre_rankings(command)
                elif (command[0] in ["recommendations", "recs"]):
                    self.recommend(command)
                elif (command[0] == "topartists"):
                    self.topartists(command)

            if (command[0]) in ["quit", "q"]:
                if self.screen in ["collections", "search", "statistics"]:
                    self.screen = "main"
                else:
                    break

            self.console.clear()
            self.render_heading()
        
        self.console.clear()
        