import asyncio
import logging
import sys
from typing import Optional

from rich.console import Console
from rich.logging import RichHandler

from .scraper import WMOOVScraper
from .processor import DataProcessor
from .date_utils import get_current_date, get_weekend_dates

# Configure logging with Rich
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(console=Console(stderr=True), rich_tracebacks=True)]
)
logger = logging.getLogger(__name__)

console = Console()


class WeekendMovieApp:
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.scraper = WMOOVScraper(headless=headless)
        
    async def run(self) -> bool:
        """Main application entry point"""
        try:
            console.print("🚀 Starting WMOOV Weekend Movie Scraper...", style="bold blue")
            
            # Initialize scraper
            await self.scraper.initialize()
            
            # Get current date and weekend info
            current_date = get_current_date()
            weekend_dates = get_weekend_dates(current_date)
            
            console.print(f"📅 Current date: {current_date.strftime('%Y-%m-%d (%A)')}")
            console.print(f"🎬 Target weekend: {weekend_dates[0].strftime('%Y-%m-%d (%A)')} - {weekend_dates[1].strftime('%Y-%m-%d (%A)')}")
            
            # Scrape movies
            console.print("\n🔍 Scraping movies with weekend showtimes...")
            movies = await self.scraper.scrape_weekend_movies()
            
            if not movies:
                console.print("[yellow]⚠️  No movies found with weekend showtimes.[/yellow]")
                return True
            
            # Display results
            console.print(f"\n✅ Found {len(movies)} movies with weekend showtimes!")
            DataProcessor.display_movies_table(movies)
            
            return True
            
        except Exception as e:
            error_msg = f"Failed to scrape movies: {str(e)}"
            logger.error(error_msg)
            DataProcessor.display_error(error_msg)
            return False
            
        finally:
            # Cleanup
            await self.scraper.close()
            console.print("\n👋 Scraper finished.")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Scrape WMOOV weekend movies and display in table format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    # Run with headless browser
  %(prog)s --no-headless     # Show browser window
  %(prog)s --verbose         # Enable detailed logging
        """
    )
    
    parser.add_argument(
        "--no-headless", 
        action="store_false", 
        dest="headless",
        help="Show browser window (useful for debugging)"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Set log level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Run the application
    app = WeekendMovieApp(headless=args.headless)
    
    try:
        success = asyncio.run(app.run())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️  Scraper interrupted by user.[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[bold red]💥 Unexpected error: {e}[/bold red]")
        sys.exit(1)


if __name__ == "__main__":
    main()