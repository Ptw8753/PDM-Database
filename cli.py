import interface

class Cli:
    def __init__(self, interface: interface):
        self.interface = interface
        

    def input_loop():
        input_str = ""

        while(input_str.strip() != "quit"):
            input_str = input()
        