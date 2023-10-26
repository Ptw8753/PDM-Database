from dataclasses import dataclass

@dataclass
class Genre:
    name: str

@dataclass
class Song:
    length: int
    title: str
    genre: Genre
    playCount: int
    #TODO make this not an int
    releaseDate: int

@dataclass
class Album:
    name: str
    songs: list[Song]
    genres: list[Genre]
    #TODO make this not an int
    releaseDate: int

@dataclass
class Artist:
    name: str

@dataclass
class Playlist:
    name: str
    songs: list[Song]
    #TODO make this not an int
    creationDate: int
