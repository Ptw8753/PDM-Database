from dataclasses import dataclass
from datetime import *


@dataclass
class Genre:
    name: str


@dataclass
class Song:
    length: int
    title: str
    genre: Genre
    playCount: int
    releaseDate: date


@dataclass
class Album:
    name: str
    songs: list[Song]
    genres: list[Genre]
    releaseDate: date


@dataclass
class Artist:
    name: str


@dataclass
class Playlist:
    name: str
    songs: list[Song]
    creationDate: date


@dataclass
class User:
    username: str
    password: str
    firstName: str
    lastName: str
    email: str
    creationDate: date
    lastAccess: datetime
