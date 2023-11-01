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
        self.loginId = None

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
* +song \[cllectionname]  
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

        self.console.print(Panel(Columns([column1, column2]), title="Command List"))

    
    def render_heading(self):
        header = """# Principles of Data Management: Music Domain
Enter "quit" or "q" to """

        if self.screen in ["collections", "search"]:
            end = """return."""
        else:
            end = """exit."""

        if self.screen == "search":
            self.console.print("Search in:")

        self.console.print(Markdown(header + end))
        self.console.print()


    def login(self, command):
        if len(command) != 3:
            self.console.print("Invalid arguments, usage: login \[username] \[password]") 
            self.console.input("Press enter to continue...")
        else:
            self.interface.loginUser(command[1], command[2])
            self.console.input("Press enter to continue...")


    def signup(self, command):
        # TODO: make new account here
        pass


    def input_loop(self):
        input_str = "null"

        while(True):
            self.print_options()
            input_str = self.console.input("> ")
            
            command = input_str.split()
            if (self.screen == "main"):
                if (command[0] == "login"):
                    self.login()

                elif (command[0] == "signup"):
                    self.signup()
                
                elif (command[0] == "collections"):
                    self.screen = "collections"

                elif (command[0] == "search"):
                    self.screen = "search"
            
            elif (self.screen == "collections"):
                pass

            elif (self.screen == "search"):
                pass

            if (command[0]) in ["quit", "q"]:
                if self.screen in ["collections", "search"]:
                    self.screen = "main"
                else:
                    break

            self.console.clear()
            self.render_heading()
        
        self.console.clear()
        