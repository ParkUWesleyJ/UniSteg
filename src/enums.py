from enum import Enum


# Used to make invalid commands/inputs more clear
class Colors(str, Enum):
    RED = "\033[91m",
    WHITE = "\033[0m"
