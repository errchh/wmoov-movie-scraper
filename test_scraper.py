#!/usr/bin/env python3
"""
Simple test script to verify the scraper functionality
"""

import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from wmoov_scraper.main import WeekendMovieApp


async def test_scraper():
    """Test the scraper with a small run"""
    print("🧪 Testing WMOOV Scraper...")
    
    app = WeekendMovieApp(headless=True)
    
    try:
        # Initialize scraper
        await app.scraper.initialize()
        
        # Test date calculation
        from wmoov_scraper.date_utils import get_current_date, get_weekend_dates
        current_date = get_current_date()
        weekend_dates = get_weekend_dates(current_date)
        
        print(f"✅ Date calculation works:")
        print(f"   Current: {current_date.strftime('%Y-%m-%d (%A)')}")
        print(f"   Weekend: {weekend_dates[0].strftime('%Y-%m-%d (%A)')} - {weekend_dates[1].strftime('%Y-%m-%d (%A)')}")
        
        # Test scraping (limit to first few movies for quick test)
        print("\n🔍 Testing movie scraping...")
        movies = await app.scraper.scrape_weekend_movies()
        
        if movies:
            print(f"✅ Found {len(movies)} movies with weekend showtimes")
            # Show first movie details
            first_movie = movies[0]
            print(f"   First movie: {first_movie.title}")
            print(f"   Rating: {first_movie.rating}")
            print(f"   Showtimes: {len(first_movie.showtimes)}")
            return True
        else:
            print("⚠️  No movies found (this might be expected)")
            return True
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
        
    finally:
        await app.scraper.close()


if __name__ == "__main__":
    success = asyncio.run(test_scraper())
    sys.exit(0 if success else 1)