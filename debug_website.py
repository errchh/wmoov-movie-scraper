#!/usr/bin/env python3
"""
Debug script to understand the website structure
"""

import asyncio
import logging
from playwright.async_api import async_playwright

from wmoov_scraper.scraper import WMOOVScraper

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


async def debug_website_structure():
    """Debug the website structure to understand selectors"""
    scraper = WMOOVScraper(headless=False)  # Show browser for debugging
    
    try:
        await scraper.initialize()
        
        # Navigate to showing movies page
        await scraper.page.goto("https://wmoov.com/movie/showing")
        await scraper.page.wait_for_load_state('networkidle')
        
        # Take a screenshot
        await scraper.page.screenshot(path="debug_screenshot.png")
        print("📸 Screenshot saved as debug_screenshot.png")
        
        # Try different selectors to find movie elements
        selectors = [
            'div.generic > div.generic > div.generic > heading',
            'h3',
            '[class*="heading"]',
            'div.movie-item',
            'div.movie-card',
            'div.film-item',
            'div.generic > heading',
            'div > div > div > heading'
        ]
        
        for selector in selectors:
            elements = await scraper.page.query_selector_all(selector)
            print(f"Selector '{selector}': {len(elements)} elements found")
            
            if elements:
                # Show first element content
                first_element = elements[0]
                text = await first_element.inner_text()
                print(f"  First element text: {repr(text[:100])}...")
        
        # Get page title and URL
        title = await scraper.page.title()
        url = scraper.page.url
        print(f"\n📄 Page Title: {title}")
        print(f"🔗 Page URL: {url}")
        
        # Get page content
        content = await scraper.page.content()
        print(f"📄 Page size: {len(content)} characters")
        
        # Look for movie-related content
        if "電影" in content or "movie" in content.lower():
            print("✅ Found movie-related content")
        else:
            print("⚠️  No obvious movie-related content found")
        
        # Look for specific patterns
        import re
        movie_patterns = [
            r'「[^」]+」',  # Movie titles in Chinese quotes
            r'[^<]+電影',   # Movies with 電影 suffix
            r'[^<]+Movie',  # Movies with Movie suffix
        ]
        
        for pattern in movie_patterns:
            matches = re.findall(pattern, content)
            print(f"Pattern '{pattern[:20]}...': {len(matches)} matches")
            if matches:
                print(f"  Sample matches: {matches[:3]}")
        
        await asyncio.sleep(10)  # Wait for manual inspection
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        
    finally:
        await scraper.close()


if __name__ == "__main__":
    asyncio.run(debug_website_structure())