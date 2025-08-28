import asyncio
import re
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from playwright.async_api import async_playwright, Page
from bs4 import BeautifulSoup
import logging

from .models import Movie, Showtime
from .date_utils import get_current_date, get_weekend_dates

logger = logging.getLogger(__name__)


class WMOOVScraper:
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.base_url = "https://wmoov.com"
        self.showing_url = f"{self.base_url}/movie/showing"
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
    
    async def scrape_weekend_movies(self) -> List[Movie]:
        """Scrape movies with weekend showtimes"""
        try:
            # Get current date and calculate weekend
            current_date = get_current_date()
            weekend_dates = get_weekend_dates(current_date)
            logger.info(f"Scraping for weekend: {weekend_dates[0]} to {weekend_dates[1]}")
            
            # Navigate to showing movies page
            await self.page.goto(self.showing_url)
            await self.page.wait_for_load_state('networkidle')
            
            # Extract movie elements
            movie_elements = await self.page.query_selector_all('h3')
            logger.info(f"Found {len(movie_elements)} movie elements using h3 selector")
            
            movies = []
            for i, element in enumerate(movie_elements):
                try:
                    # Extract title directly without navigating
                    title_text = await element.inner_text()
                    title = title_text.strip()
                    
                    # Clean up title - extract just the movie name
                    # Format: "「鬼滅之刃」無限城篇 熱門 主打 好評"
                    import re
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
                        continue
                    
                    logger.debug(f"Processing movie {i+1}/{len(movie_elements)}: {title}")
                    
                    # Find the actual movie link from the h3 element
                    movie_link = await element.query_selector('a')
                    if movie_link:
                        movie_href = await movie_link.get_attribute('href')
                        if movie_href and movie_href.startswith('/movie/details/'):
                            movie_url = movie_href
                            movie_id = movie_href.split('/')[-1]
                        else:
                            # Fallback to generated URL
                            movie_id = hash(title) % 100000
                            movie_url = f"/movie/details/{movie_id}"
                    else:
                        # Fallback to generated URL
                        movie_id = hash(title) % 100000
                        movie_url = f"/movie/details/{movie_id}"
                    
                    logger.debug(f"Movie URL: {movie_url} (ID: {movie_id})")
                    
                    # Find parent container to get more info
                    parent = await element.query_selector('..')
                    if not parent:
                        continue
                    
                    # Extract rating - look for rating in parent or siblings
                    rating = None
                    rating_elements = await parent.query_selector_all('link')
                    for rating_element in rating_elements:
                        rating_text = await rating_element.inner_text()
                        if rating_text and rating_text.replace('.', '').isdigit():
                            rating = float(rating_text)
                            break
                    
                    # Extract genres
                    genres = []
                    genre_elements = await parent.query_selector_all(':text-is("片種:")')
                    if genre_elements:
                        genre_text = await genre_elements[0].inner_text()
                        genres = self._extract_genres(genre_text)
                    
                    # Extract popularity
                    popularity = 0
                    popularity_elements = await parent.query_selector_all(':text-is("人氣:")')
                    if popularity_elements:
                        popularity_text = await popularity_elements[0].inner_text()
                        popularity = self._extract_popularity(popularity_text)
                    
                    movie = Movie(
                        title=title,
                        rating=rating,
                        genres=genres,
                        director=None,  # Would need more detailed scraping
                        cast=[],        # Would need more detailed scraping
                        popularity=popularity,
                        showtimes=[],   # Will be populated later
                        url=movie_url
                    )
                    
                    # Get detailed showtimes for this movie in a new tab
                    showtimes = await self._scrape_movie_showtimes(movie, weekend_dates)
                    if showtimes:
                        movie.showtimes = showtimes
                        movies.append(movie)
                        logger.info(f"Found {len(showtimes)} showtimes for: {movie.title}")
                    
                except Exception as e:
                    logger.warning(f"Failed to extract movie info for element {i+1}: {e}")
                    continue
            
            logger.info(f"Successfully scraped {len(movies)} movies with weekend showtimes")
            return movies
            
        except Exception as e:
            logger.error(f"Error during scraping: {e}")
            raise
    
    async def _extract_movie_info(self, element) -> Optional[Movie]:
        """Extract basic movie information from element"""
        try:
            # Extract title from h3 text
            title_text = await element.inner_text()
            title = title_text.strip()
            
            # Clean up title - extract just the movie name
            # Format: "「鬼滅之刃」無限城篇 熱門 主打 好評"
            import re
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
            
            logger.debug(f"Processing movie: {title}")
            
            # Find parent container to get more info
            parent = await element.query_selector('..')
            if not parent:
                return None
            
            # Extract rating - look for rating in parent or siblings
            rating = None
            rating_elements = await parent.query_selector_all('link')
            for rating_element in rating_elements:
                rating_text = await rating_element.inner_text()
                if rating_text and rating_text.replace('.', '').isdigit():
                    rating = float(rating_text)
                    break
            
            # Extract genres
            genres = []
            genre_elements = await parent.query_selector_all(':text-is("片種:")')
            if genre_elements:
                genre_text = await genre_elements[0].inner_text()
                genres = self._extract_genres(genre_text)
            
            # Extract popularity
            popularity = 0
            popularity_elements = await parent.query_selector_all(':text-is("人氣:")')
            if popularity_elements:
                popularity_text = await popularity_elements[0].inner_text()
                popularity = self._extract_popularity(popularity_text)
            
            # Create a proper URL for movie details page
            movie_id = hash(title) % 100000
            movie_url = f"/movie/details/{movie_id}"
            
            return Movie(
                title=title,
                rating=rating,
                genres=genres,
                director=None,  # Would need more detailed scraping
                cast=[],        # Would need more detailed scraping
                popularity=popularity,
                showtimes=[],   # Will be populated later
                url=movie_url
            )
            
        except Exception as e:
            logger.warning(f"Failed to extract movie info: {e}")
            return None
    
    def _parse_rating(self, rating_text: str) -> Optional[float]:
        """Parse rating from text"""
        try:
            match = re.search(r'(\d+\.?\d*)', rating_text)
            return float(match.group(1)) if match else None
        except:
            return None
    
    def _extract_showtimes_count(self, text: str) -> int:
        """Extract number of showtimes from text"""
        match = re.search(r'共(\d+)場', text)
        return int(match.group(1)) if match else 0
    
    def _extract_genres(self, text: str) -> List[str]:
        """Extract genres from text"""
        try:
            # Extract text after "片種:"
            match = re.search(r'片種:\s*(.*)', text)
            if match:
                genres_text = match.group(1).strip()
                return [genre.strip() for genre in genres_text.split(',')]
        except:
            pass
        return []
    
    def _extract_popularity(self, text: str) -> int:
        """Extract popularity count from text"""
        try:
            match = re.search(r'人氣:\s*(\d+)', text)
            return int(match.group(1)) if match else 0
        except:
            return 0
    
    async def _scrape_movie_showtimes(self, movie: Movie, weekend_dates: List[date]) -> List[Showtime]:
        """Scrape showtimes for specific movie on weekend dates"""
        try:
            movie_url = getattr(movie, 'url', None)
            if not movie_url:
                return []
                
            full_url = f"{self.base_url}{movie_url}"
            logger.info(f"Scraping showtimes for {movie.title} from {full_url}")
            
            # Open new tab for movie details to avoid context issues
            new_page = await self.context.new_page()
            try:
                await new_page.goto(full_url)
                await new_page.wait_for_load_state('networkidle')
                
                showtimes = []
                
                # Navigate to date picker and select weekend dates
                date_selector = await new_page.query_selector('combobox[ref=e61]')
                if not date_selector:
                    logger.warning(f"Date selector not found for movie: {movie.title}")
                    return []
                
                await date_selector.click()
                
                for weekend_date in weekend_dates:
                    # Format date for selector - format is "8月30日 星期六"
                    date_str = weekend_date.strftime("%m月%d日 %A")
                    
                    # Find and select the date option
                    date_option = await new_page.query_selector(f'option:has-text("{date_str}")')
                    if date_option:
                        await date_option.click()
                        await new_page.wait_for_timeout(1000)
                        
                        # Extract showtimes from table
                        table_showtimes = await self._extract_table_showtimes(new_page, weekend_date)
                        showtimes.extend(table_showtimes)
                
                return showtimes
                
            finally:
                await new_page.close()
                
        except Exception as e:
            logger.warning(f"Failed to scrape showtimes for {movie.title}: {e}")
            return []
    
    async def _extract_table_showtimes(self, page, target_date: date) -> List[Showtime]:
        """Extract showtimes from the showtimes table"""
        try:
            showtimes = []
            
            # Find the showtimes table
            table = await page.query_selector('table[ref=e65]')
            if not table:
                return showtimes
            
            # Get all rows (skip header)
            rows = await table.query_selector_all('tr')
            
            for row in rows[1:]:  # Skip header row
                try:
                    cells = await row.query_selector_all('td')
                    if len(cells) >= 5:
                        showtime = await self._parse_showtime_row(cells, target_date)
                        if showtime:
                            showtimes.append(showtime)
                except Exception as e:
                    logger.warning(f"Failed to parse showtime row: {e}")
                    continue
            
            return showtimes
            
        except Exception as e:
            logger.warning(f"Failed to extract table showtimes: {e}")
            return []
    
    async def _parse_showtime_row(self, cells, target_date: date) -> Optional[Showtime]:
        """Parse individual showtime row"""
        try:
            # Extract cinema and hall information
            cinema_text = await cells[0].inner_text()
            
            # Extract hall information (usually in parentheses)
            hall_match = re.search(r'\(([^)]+)\)', cinema_text)
            hall = hall_match.group(1) if hall_match else ""
            cinema_name = re.sub(r'\s*\([^)]+\)', '', cinema_text).strip()
            
            # Extract time
            time_text = await cells[1].inner_text()
            time_match = re.search(r'(\d{1,2}):(\d{2})\s*(AM|PM)', time_text)
            if time_match:
                hour, minute, period = time_match.groups()
                hour = int(hour)
                if period == 'PM' and hour != 12:
                    hour += 12
                elif period == 'AM' and hour == 12:
                    hour = 0
                time_str = f"{hour:02d}:{minute}"
            else:
                time_str = time_text.strip()
            
            # Extract available seats
            seats_text = await cells[2].inner_text()
            seats_available = seats_text.split()[0] if seats_text else "未知"
            
            # Extract price
            price_text = await cells[3].inner_text()
            price_match = re.search(r'\$?(\d+)', price_text)
            price = float(price_match.group(1)) if price_match else 0.0
            
            # Get booking URL
            booking_link = await cells[4].query_selector('link')
            booking_url = await booking_link.get_attribute('href') if booking_link else None
            
            return Showtime(
                cinema=cinema_name,
                hall=hall,
                time=time_str,
                date=target_date.strftime('%Y-%m-%d'),
                available_seats=seats_available,
                price=price,
                booking_url=booking_url
            )
            
        except Exception as e:
            logger.warning(f"Failed to parse showtime row: {e}")
            return None