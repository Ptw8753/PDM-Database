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

        self.startup()
        self.input_loop()


    def print_options(self):
        if self.screen == "main":
            column1 ="""
* login \[username] \[password]  
* signup  
* collections  
* search \[songname]  
"""
            column2 ="""
* listen \[songname] or \[albumname]  
* follow \[useremail]  
* unfollow \[useremail]  
* help \[command]  
"""
        elif self.screen == "collections":
            column1 ="""
* create \[name]  
* +album \[collectionname]  
* +song \[cllectionname]  
* editname \[name] \[newname]  
"""

            column2 ="""
* delete \[name]  
* -album \[collectionname]  
* -song \[collectionname]  
* listen \[collectionname]  
"""
        self.console.print(Panel(Columns([column1, column2]), title="Command List"))

    
    def render_heading(self):
        header = """# Principles of Data Management: Music Domain"""
        self.console.print(Markdown(header))


    def startup(self):
        self.render_heading()
        self.console.print()


    def input_loop(self):
        input_str = "null"

        while(input_str.split()[0] not in ["quit", "q"]):
            self.print_options()
            input_str = self.console.input("> ")
            
            command = input_str.split()
            if (command[0] == "login"):
                if len(command) != 3:
                    self.console.print("Invalid arguments, usage: login \[username] \[password]") 
                    self.console.input("Press enter to continue...")
                else:
                    self.interface.loginUser(command[1], command[2])
                    self.console.input("Press enter to continue...")
            
            if (command[0] == "collections"):
                self.screen = "collections"

            self.console.clear()
            self.render_heading()
        
        self.console.clear()
        