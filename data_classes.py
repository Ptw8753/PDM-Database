from dataclasses import dataclass
from datetime import *

@dataclass
class Song:
    title: str
    artistName: str
    albumNames: list[str]
    genres: list[str]
    length: int
    listenCount: int

@dataclass
class User:
    username: str
    password: str
    firstName: str
    lastName: str
    email: str
    creationDate: date
    lastAccess: datetime