<<<<<<< HEAD
# wmoov-movie-scraper
=======
# WMOOV Weekend Movie Scraper

A Python web scraper that fetches movies playing in Hong Kong cinemas during the upcoming weekend from WMOOV (https://wmoov.com/).

## Features

- 🎬 Scrapes currently showing movies from WMOOV
- 📅 Automatically calculates upcoming Saturday and Sunday
- 🎭 Filters movies with weekend showtimes
- 📊 Displays results in beautiful table format
- 🚀 Uses Playwright for reliable web scraping
- 💻 Headless mode by default (browser runs in background)
- ⚡ Fast and efficient with concurrent processing

## Installation

1. Install UV (Python package manager):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Install project dependencies:
```bash
uv sync
```

3. Install Playwright browsers:
```bash
playwright install chromium
```

## Usage

### Basic Usage
```bash
# Run scraper (headless mode by default)
uv run wmoov-scraper

# Show browser window for debugging
uv run wmoov-scraper --no-headless

# Enable verbose logging
uv run wmoov-scraper --verbose
```

### Direct Python execution
```bash
python -m wmoov_scraper.main
```

## Output Format

The scraper displays movie information in a formatted table:

```
🎬 Weekend Movies - WMOOV
┌───────────────────────────┬──────────┬─────────────────────┬─────────────────────────┬─────────────────────────────┬──────────────┐
│ Movie Title               │ Rating   │ Genres              │ Cinemas                │ Showtimes                   │ Price Range  │
├───────────────────────────┼──────────┼─────────────────────┼─────────────────────────┼─────────────────────────────┼──────────────┤
│ 「鬼滅之刃」無限城篇     │ 9.1      │ 動畫,動作,奇幻      │ 百老匯 MOViE MOViE     │ 百老匯 MOViE MOViE: 07:30  │ $120-130     │
│                           │          │                     │ Cinema City            │                            │              │
│ 東極島                   │ 6.2      │ 劇情                │                        │                            │ $100-110     │
└───────────────────────────┴──────────┴─────────────────────┴─────────────────────────┴─────────────────────────────┴──────────────┘

📊 Summary
┌─────────────────────────────────────────────────────────────────┐
│ 📅 Weekend: 2025-08-30 to 2025-08-31                           │
│ 🎭 Total Movies: 2                                              │
│ ⏰ Total Showtimes: 5                                           │
│ 🕒 Scraped: 2025-08-28 10:30                                   │
└─────────────────────────────────────────────────────────────────┘
```

## Project Structure

```
wmoov_scraper/
├── __init__.py
├── main.py              # Main application entry point
├── scraper.py           # Web scraping logic
├── models.py            # Data models
├── processor.py         # Data processing and display
├── date_utils.py        # Date calculation utilities
└── pyproject.toml       # Project configuration
```

## Dependencies

- **playwright**: Browser automation for web scraping
- **rich**: Beautiful terminal formatting and tables
- **typer**: CLI interface
- **python-dateutil**: Date manipulation utilities

## Error Handling

The scraper includes comprehensive error handling:

- Network timeouts and connection errors
- Missing elements on the page
- Data parsing failures
- Browser automation issues

In case of errors, the scraper will display a concise error message and exit gracefully.

## Date Calculation

The scraper automatically determines the upcoming weekend:

- **Weekend**: Saturday + Sunday
- **Calculation**: Finds the next Saturday from the current date
- **Example**: If today is Thursday, it calculates this Saturday and Sunday

## Requirements

- Python 3.8+
- UV package manager
- Internet connection
- WMOOV website accessibility

## Development

### Running Tests
```bash
uv run pytest
```

### Code Formatting
```bash
uv run black .
uv run ruff check .
```

## License

This project is for educational and personal use only. Please respect WMOOV's terms of service and robots.txt.
>>>>>>> 820b64a (Initial commit)
