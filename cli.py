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
        input_str = ""

        while(input_str.strip() not in ["quit", "q"]):
            
            


            input_str = self.console.input("> ")
        