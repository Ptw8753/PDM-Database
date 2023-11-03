from dataclasses import dataclass
from datetime import *

@dataclass
class Song:
    title: str
    artistNames: list[str]
    albumNames: list[str]
    genres: list[str]
    length: int
    listenCount: int
