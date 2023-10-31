from db_interface import Interface

# if this breaks for you, do "python -m pip install rich"
from rich import print
from rich.console import Console
from rich.markdown import Markdown

class Cli:
    def __init__(self, interface: Interface):
        self.interface = interface
        self.console = Console()

        self.startup()
        self.input_loop()


    def startup(self):
        MARKDOWN = """
        # Principles of Data Management
        ## Music Domain

        Welcome! Please selection option from the below list:
        * option a
        * option b
        * option c
        """
        self.console.print(Markdown(MARKDOWN))


    def input_loop(self):
        input_str = ""

        while(input_str.strip() != "quit" and input_str.strip() != "q"):
            
            


            input_str = self.console.input()
        