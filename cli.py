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

        self.startup()
        self.input_loop()


    def startup(self):
        header = """# Principles of Data Management: Music Domain

Welcome! Please selection option from the below list:
"""
        
        column1 ="""
* option a  
* option b  
* option c  
* option d  
"""
        column2 ="""
* option e  
* option f  
* option g  
* option h  
"""

        # add more columns if needed
        columns = Columns([column1, column2])

        self.console.print(Markdown(header))
        self.console.print("\n")
        self.console.print(Panel(columns, title="Command List"))
        self.console.print()


    def input_loop(self):
        input_str = "null"

        while(input_str):

            input_str = self.console.input("> ")

            # give user quit prompt it the enter nothing or quit or q
            if not input_str or input_str.split()[0] in ["quit", "q"]:
                d = self.console.input("Are you sure you want to quit? (y/n) ")
                if d in ["Y", "y"]:
                    break
                else:
                    input_str = "null"

        self.console.clear()
        