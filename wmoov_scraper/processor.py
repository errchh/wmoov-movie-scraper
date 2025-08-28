from typing import List, Dict, Any
import logging
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from .models import Movie, Showtime
from .date_utils import get_current_date, get_weekend_dates

logger = logging.getLogger(__name__)


class DataProcessor:
    @staticmethod
    def format_for_display(movies: List[Movie]) -> Dict[str, Any]:
        """Format movie data for display"""
        current_date = get_current_date()
        weekend_dates = get_weekend_dates(current_date)
        
        return {
            "scraped_at": datetime.now().isoformat(),
            "weekend_dates": [d.strftime('%Y-%m-%d') for d in weekend_dates],
            "total_movies": len(movies),
            "movies": movies
        }
    
    @staticmethod
    def display_movies_table(movies: List[Movie]):
        """Display movies in a formatted table"""
        if not movies:
            console = Console()
            console.print("[yellow]No movies found with weekend showtimes.[/yellow]")
            return
        
        console = Console()
        
        # Create main table
        table = Table(title="🎬 Weekend Movies - WMOOV", show_header=True, header_style="bold magenta")
        table.add_column("Movie Title", style="cyan", width=30)
        table.add_column("Rating", style="green", width=8)
        table.add_column("Genres", style="yellow", width=20)
        table.add_column("Cinemas", style="blue", width=25)
        table.add_column("Showtimes", style="magenta", width=30)
        table.add_column("Price Range", style="red", width=12)
        
        for movie in movies:
            # Format rating
            rating_str = f"{movie.rating}" if movie.rating else "N/A"
            
            # Format genres
            genres_str = ", ".join(movie.genres[:3])  # Show first 3 genres
            if len(movie.genres) > 3:
                genres_str += "..."
            
            # Format cinemas and showtimes
            cinema_showtimes = {}
            for showtime in movie.showtimes:
                if showtime.cinema not in cinema_showtimes:
                    cinema_showtimes[showtime.cinema] = []
                cinema_showtimes[showtime.cinema].append(showtime.time)
            
            cinemas_str = ", ".join(list(cinema_showtimes.keys())[:3])  # Show first 3 cinemas
            if len(cinema_showtimes) > 3:
                cinemas_str += "..."
            
            # Format showtimes
            all_showtimes = []
            for cinema, times in cinema_showtimes.items():
                all_showtimes.extend([f"{cinema}: {t}" for t in times[:2]])  # Show 2 times per cinema
            if len(all_showtimes) > 6:  # Limit total showtimes displayed
                all_showtimes = all_showtimes[:6] + ["..."]
            
            showtimes_str = "\n".join(all_showtimes[:4])  # Show first 4 in table
            
            # Calculate price range
            prices = [s.price for s in movie.showtimes]
            min_price = min(prices) if prices else 0
            max_price = max(prices) if prices else 0
            price_str = f"${min_price}-{max_price}" if min_price != max_price else f"${min_price}"
            
            table.add_row(
                movie.title[:29],  # Truncate if too long
                rating_str,
                genres_str[:19],  # Truncate if too long
                cinemas_str[:24],  # Truncate if too long
                showtimes_str[:29],  # Truncate if too long
                price_str
            )
        
        console.print(table)
        
        # Print summary information
        weekend_dates = get_weekend_dates(get_current_date())
        summary_text = f"📅 Weekend: {weekend_dates[0].strftime('%Y-%m-%d')} to {weekend_dates[1].strftime('%Y-%m-%d')}\n"
        summary_text += f"🎭 Total Movies: {len(movies)}\n"
        summary_text += f"⏰ Total Showtimes: {sum(len(m.showtimes) for m in movies)}\n"
        summary_text += f"🕒 Scraped: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        summary_panel = Panel(summary_text, title="📊 Summary", border_style="blue")
        console.print(summary_panel)
        
        # Print detailed showtimes for each movie
        for movie in movies:
            if movie.showtimes:
                movie_panel = DataProcessor._create_movie_detail_panel(movie)
                console.print(movie_panel)
    
    @staticmethod
    def _create_movie_detail_panel(movie: Movie) -> Panel:
        """Create detailed panel for individual movie"""
        from rich.text import Text
        
        # Format showtimes by cinema
        cinema_info = {}
        for showtime in movie.showtimes:
            if showtime.cinema not in cinema_info:
                cinema_info[showtime.cinema] = []
            cinema_info[showtime.cinema].append(showtime)
        
        details = Text()
        details.append(f"🎬 {movie.title}\n", style="bold cyan")
        
        if movie.rating:
            details.append(f"⭐ Rating: {movie.rating}\n", style="yellow")
        
        if movie.genres:
            details.append(f"🎭 Genres: {', '.join(movie.genres)}\n", style="green")
        
        details.append("🎪 Showtimes:\n", style="bold magenta")
        
        for cinema, showtimes in cinema_info.items():
            details.append(f"  {cinema}\n", style="blue")
            for showtime in showtimes:
                details.append(f"    {showtime.time} - ${showtime.price} ({showtime.available_seats})\n", style="white")
        
        return Panel(details, title=f"📋 {movie.title}", border_style="cyan")
    
    @staticmethod
    def display_error(error_message: str):
        """Display error message"""
        console = Console()
        console.print(f"[bold red]❌ Error: {error_message}[/bold red]")
    
    @staticmethod
    def display_no_data():
        """Display message when no data is available"""
        console = Console()
        console.print("[yellow]ℹ️  No weekend movie data available.[/yellow]")