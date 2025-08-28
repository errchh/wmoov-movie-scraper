#!/usr/bin/env python3
"""
Final working scraper for WMOOV weekend movies
"""

import asyncio
import logging
import re
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

from playwright.async_api import async_playwright, Page
from rich.console import Console
from rich.table import Table

console = Console()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class SimpleMovie:
    title: str
    rating: Optional[float]
    genres: List[str]
    popularity: int
    url: Optional[str]


@dataclass
class SimpleShowtime:
    cinema: str
    time: str
    date: str
    price: float
    available_seats: str


class SimpleWMOOVScraper:
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.base_url = "https://wmoov.com"
        self.page: Optional[Page] = None
        self.playwright = None
        self.browser = None
        self.context = None
        
    async def initialize(self):
        """Initialize Playwright browser"""
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(headless=self.headless)
            self.context = await self.browser.new_context()
            self.page = await self.context.new_page()
            logger.info("Browser initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize browser: {e}")
            raise
    
    async def close(self):
        """Close browser and cleanup"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        logger.info("Browser closed")
    
    async def scrape_weekend_movies(self) -> List[SimpleMovie]:
        """Scrape currently showing movies"""
        try:
            # Navigate to showing movies page
            await self.page.goto("https://wmoov.com/movie/showing")
            await self.page.wait_for_load_state('networkidle')
            
            # Extract movie elements
            movie_elements = await self.page.query_selector_all('h3')
            
            movies = []
            for element in movie_elements:
                try:
                    movie = await self._extract_movie_info(element)
                    if movie:
                        movies.append(movie)
                except Exception as e:
                    logger.warning(f"Failed to extract movie: {e}")
                    continue
            
            logger.info(f"Successfully extracted {len(movies)} movies")
            return movies
            
        except Exception as e:
            logger.error(f"Error during scraping: {e}")
            raise
    
    async def _extract_movie_info(self, element) -> Optional[SimpleMovie]:
        """Extract basic movie information from element"""
        try:
            # Extract title from h3 text
            title_text = await element.inner_text()
            title = title_text.strip()
            
            # Clean up title - extract just the movie name
            # Format: "「鬼滅之刃」無限城篇 熱門 主打 好評"
            movie_match = re.match(r'「([^」]+)」', title)
            if movie_match:
                title = movie_match.group(1)
            else:
                # Try to extract without quotes
                parts = title.split()
                if len(parts) > 0:
                    title = parts[0]
            
            # Skip if title is too short or not a movie
            if not title or len(title) < 2 or title in ['即日上映', '即將上映', '戲院', '預告']:
                return None
            
            # Find parent container to get more info
            parent = await element.query_selector('..')
            if not parent:
                return None
            
            # Extract rating from div.rating > a > b
            rating = None
            rating_element = await parent.query_selector('div.rating b')
            if rating_element:
                rating_text = await rating_element.inner_text()
                if rating_text and rating_text.replace('.', '').isdigit():
                    rating = float(rating_text)
            
            # Extract genres
            genres = []
            # Look for genres in the page content
            page_content = await self.page.content()
            genre_patterns = [
                rf'{title}[^<]*片種:([^<]+)',
                rf'{title}[^<]*片種\s*[:：]([^<]+)'
            ]
            
            for pattern in genre_patterns:
                match = re.search(pattern, page_content, re.IGNORECASE)
                if match:
                    genres_text = match.group(1).strip()
                    genres = [g.strip() for g in genres_text.split(',')]
                    break
            
            # Extract popularity from p element containing 人氣:
            popularity = 0
            popularity_patterns = [
                r'人氣:\s*([\d,]+)',
                r'人氣\s*[:：]\s*([\d,]+)'
            ]
            
            # Try to find popularity in the parent text
            parent_text = await parent.inner_text()
            for pattern in popularity_patterns:
                popularity_match = re.search(pattern, parent_text)
                if popularity_match:
                    popularity_text = popularity_match.group(1).replace(',', '')
                    popularity = int(popularity_text)
                    break
            
            # If not found in parent, try page content
            if popularity == 0:
                for pattern in popularity_patterns:
                    popularity_match = re.search(pattern, page_content, re.IGNORECASE)
                    if popularity_match:
                        popularity_text = popularity_match.group(1).replace(',', '')
                        popularity = int(popularity_text)
                        break
            
            # Create a proper URL (placeholder)
            movie_id = hash(title) % 100000
            movie_url = f"{self.base_url}/movie/details/{movie_id}"
            
            return SimpleMovie(
                title=title,
                rating=rating,
                genres=genres,
                popularity=popularity,
                url=movie_url
            )
            
        except Exception as e:
            logger.warning(f"Failed to extract movie info: {e}")
            return None


def get_current_date():
    """Get current date in Hong Kong timezone"""
    from datetime import datetime
    import pytz
    return datetime.now(pytz.timezone('Asia/Hong_Kong')).date()


def get_weekend_dates(current_date):
    """
    Calculate upcoming weekend dates (Saturday + Sunday)
    """
    # Find next Saturday
    days_until_saturday = (5 - current_date.weekday()) % 7
    if days_until_saturday == 0 and current_date.weekday() != 5:
        days_until_saturday = 7
    
    saturday = current_date + timedelta(days=days_until_saturday)
    sunday = saturday + timedelta(days=1)
    
    return [saturday, sunday]


def display_movies_table(movies: List[SimpleMovie]):
    """Display movies in a formatted table with Title, Rating, Popularity columns ordered by Rating"""
    if not movies:
        console.print("[yellow]No movies found.[/yellow]")
        return
    
    # Sort movies by rating (highest first)
    sorted_movies = sorted(movies, key=lambda x: x.rating or 0, reverse=True)
    
    # Create main table
    table = Table(title="🎬 Weekend Movies - WMOOV (Ordered by Rating)", show_header=True, header_style="bold magenta")
    table.add_column("Movie Title", style="cyan", width=50)
    table.add_column("Rating", style="green", width=10)
    table.add_column("Popularity", style="blue", width=12)
    
    for movie in sorted_movies:
        # Format rating
        rating_str = f"{movie.rating}" if movie.rating else "N/A"
        
        # Format popularity
        popularity_str = f"{movie.popularity}" if movie.popularity > 0 else "N/A"
        
        table.add_row(
            movie.title[:49],  # Truncate if too long
            rating_str,
            popularity_str
        )
    
    console.print(table)


async def main():
    """Main application entry point"""
    try:
        console.print("🚀 Starting WMOOV Weekend Movie Scraper...", style="bold blue")
        
        # Initialize scraper
        scraper = SimpleWMOOVScraper(headless=True)
        await scraper.initialize()
        
        # Get current date and weekend info
        current_date = get_current_date()
        weekend_dates = get_weekend_dates(current_date)
        
        console.print(f"📅 Current date: {current_date.strftime('%Y-%m-%d (%A)')}")
        console.print(f"🎬 Target weekend: {weekend_dates[0].strftime('%Y-%m-%d (%A)')} - {weekend_dates[1].strftime('%Y-%m-%d (%A)')}")
        
        # Scrape movies
        console.print("\n🔍 Scraping currently showing movies...")
        movies = await scraper.scrape_weekend_movies()
        
        if not movies:
            console.print("[yellow]⚠️  No movies found.[/yellow]")
            return
        
        console.print(f"\n✅ Found {len(movies)} movies!")
        display_movies_table(movies)
        
        # Print summary
        summary_text = f"📅 Weekend: {weekend_dates[0].strftime('%Y-%m-%d')} to {weekend_dates[1].strftime('%Y-%m-%d')}\n"
        summary_text += f"🎭 Total Movies: {len(movies)}\n"
        summary_text += f"🕒 Scraped: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        console.print(f"\n[bold blue]{summary_text}[/bold blue]")
        
    except Exception as e:
        console.print(f"[bold red]❌ Error: {str(e)}[/bold red]")
        logger.error(f"Scraping failed: {e}")
        
    finally:
        await scraper.close()
        console.print("\n👋 Scraper finished.")


if __name__ == "__main__":
    asyncio.run(main())