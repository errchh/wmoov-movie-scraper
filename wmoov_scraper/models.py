from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime


@dataclass
class Showtime:
    cinema: str
    hall: str
    time: str
    date: str
    available_seats: str
    price: float
    booking_url: Optional[str] = None


@dataclass
class Movie:
    title: str
    rating: Optional[float]
    genres: List[str]
    director: Optional[str]
    cast: List[str]
    popularity: int
    showtimes: List[Showtime]
    url: Optional[str] = None
    poster_url: Optional[str] = None
    trailer_url: Optional[str] = None