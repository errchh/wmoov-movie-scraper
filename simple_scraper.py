#!/usr/bin/env python3
"""
Simple working scraper that extracts basic movie information
"""

import asyncio
import logging
from rich.console import Console

from wmoov_scraper.scraper import WMOOVScraper
from wmoov_scraper.processor import DataProcessor
from wmoov_scraper.date_utils import get_current_date, get_weekend_dates

console = Console()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def simple_scraper():
    """Simple scraper that extracts basic movie information"""
    scraper = WMOOVScraper(headless=True)
    
    try:
        console.print("🚀 Starting Simple WMOOV Scraper...", style="bold blue")
        
        # Initialize scraper
        await scraper.initialize()
        
        # Get current date and weekend info
        current_date = get_current_date()
        weekend_dates = get_weekend_dates(current_date)
        
        console.print(f"📅 Current date: {current_date.strftime('%Y-%m-%d (%A)')}")
        console.print(f"🎬 Target weekend: {weekend_dates[0].strftime('%Y-%m-%d (%A)')} - {weekend_dates[1].strftime('%Y-%m-%d (%A)')}")
        
        # Navigate to showing movies page
        console.print("\n🔍 Navigating to WMOOV showing movies page...")
        await scraper.page.goto("https://wmoov.com/movie/showing")
        await scraper.page.wait_for_load_state('networkidle')
        
        # Extract movie elements
        movie_elements = await scraper.page.query_selector_all('h3')
        console.print(f"📺 Found {len(movie_elements)} movie elements")
        
        movies = []
        for i, element in enumerate(movie_elements[:10]):  # Limit to first 10 for testing
            try:
                movie = await scraper._extract_movie_info(element)
                if movie:
                    movies.append(movie)
            except Exception as e:
                logger.warning(f"Failed to extract movie {i}: {e}")
                continue
        
        console.print(f"\n📊 Successfully extracted {len(movies)} movies:")
        
        # Display basic info
        for movie in movies:
            info = f"🎬 {movie.title}"
            if movie.rating:
                info += f" (⭐ {movie.rating})"
            if movie.genres:
                info += f" 🎭 {', '.join(movie.genres[:2])}"
            if movie.popularity > 0:
                info += f" 👍 {movie.popularity}"
            
            console.print(info)
        
        # Show summary
        console.print(f"\n📈 Summary:")
        console.print(f"   Total movies found: {len(movie_elements)}")
        console.print(f"   Movies extracted: {len(movies)}")
        console.print(f"   Weekend: {weekend_dates[0].strftime('%Y-%m-%d')} to {weekend_dates[1].strftime('%Y-%m-%d')}")
        
        return movies
        
    except Exception as e:
        console.print(f"[bold red]❌ Error: {str(e)}[/bold red]")
        logger.error(f"Scraper failed: {e}")
        return []
        
    finally:
        await scraper.close()
        console.print("\n👋 Scraper finished.")


if __name__ == "__main__":
    asyncio.run(simple_scraper())