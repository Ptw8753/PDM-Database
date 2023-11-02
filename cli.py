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
* collections  
* search
"""
            column2 ="""[bright_green]
* listen \[songname] or \[albumname]  
* follow \[useremail]  
* unfollow \[useremail]  
* help \[command]  
"""
        elif self.screen == "collections":
            column1 ="""[bright_red]
* create \[name]  
* +album \[collectionname]  
* +song \[collectionname]  
* editname \[name] \[newname]  
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

        if self.screen != "collections":
            self.console.print(Panel(Columns([column1, column2]), title="Command List"))
        else:
            self.console.print(Columns(
                [Panel(Columns([column1, column2]), title="Command List"), 
                 Panel(Columns(self.render_collections()), title="Collections")]))

    
    def render_heading(self):
        header = """# Principles of Data Management: Music Domain
Enter "quit" or "q" to """

        if self.screen in ["collections", "search"]:
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

            if collections == []:
                return ["You have no collections."]

        i = 0
        for collection in collections:
            column += "\n" + line_start + collection[0] + "  "
            i += 1

            if i % 4 == 0:
                column += "\n"
                columns.append(column)
                column = "[bright_red]"

            elif i == len(collections):
                columns += "\n"

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

    def help(self, command):
        # TODO
        # maybe we do this, not needed
        pass


    def create(self, command):
        name = self.stringify(command[1:])

        if (self.login_id == None):
            self.console.print("Log in to create a playlist.")
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
        # TODO
        pass


    def add_album(self, command):
        # TODO 
        pass


    def delete_album(self, command):
        # TODO
        pass


    def add_song(self, command):
        # TODO
        pass


    def delete_song(self, command):
        # TODO
        pass


    def edit_name(self, command):
        # TODO
        pass


    def listen_collection(self, command):
        # TODO
        pass


    # search command goes as follows
    # seach <subject> <keyword> optional=<order by>

    def search_songs(self, command):
        # search songs <keyword> optional<sort> optional<ASC/DESC>
        songs = list()
        if len(command) == 5:
            pass
        pass

    def search_albums(self, command):
        # search albums <keyword> optional<sort> optional<ASC/DESC>
        songs = list()
        if len(command) == 5:
            pass
        pass



    def search_artists(self, command):
        # search artists <keyword> optional<sort> optional<ASC/DESC>
        songs = list()
        if len(command) == 5:
            pass
        pass



    def search_genres(self, command):
        # search genres <keyword> optional<sort> optional<ASC/DESC>
        songs = list()
        if len(command) == 5:
            pass
        pass



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

                elif (command[0] == "follow"):
                    self.follow(command)
                
                elif (command[0] == "unfollow"):
                    self.unfollow(command)

                elif (command[0] == "help"):
                    self.console.print("Not implemented.")
                    self.console.input("Press enter to continue...")
            
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

                elif (command[0] == "editname"):
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

            if (command[0]) in ["quit", "q"]:
                if self.screen in ["collections", "search"]:
                    self.screen = "main"
                else:
                    break

            self.console.clear()
            self.render_heading()
        
        self.console.clear()
        