from db_interface import Interface

class Cli:
    def __init__(self, interface: Interface):
        self.interface = interface
        self.input_loop()


    def input_loop(self):
        input_str = ""

        while(input_str.strip() != "quit"):
            input_str = input()
        