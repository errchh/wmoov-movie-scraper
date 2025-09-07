# WMOOV Weekend Movie Scraper

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A modern Python web scraper that fetches movies playing in Hong Kong cinemas during the upcoming weekend from [WMOOV](https://wmoov.com/). Built with reliability and efficiency in mind.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Output Format](#output-format)
- [Project Structure](#project-structure)
- [Dependencies](#dependencies)
- [Error Handling](#error-handling)
- [Date Calculation](#date-calculation)
- [Requirements](#requirements)
- [Development](#development)
- [License](#license)

## Features

- **Automated Scraping**: Fetches currently showing movies from WMOOV
- **Smart Date Handling**: Automatically calculates the upcoming Saturday and Sunday
- **Weekend Filtering**: Filters movies with available weekend showtimes
- **Rich Display**: Presents results in a beautifully formatted table
- **Reliable Automation**: Uses Playwright for robust web scraping
- **Headless Mode**: Runs in background by default for efficiency
- **Concurrent Processing**: Optimized for speed and performance

## Installation

1. **Install UV** (Modern Python package manager):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Install Dependencies**:
   ```bash
   uv sync
   ```

3. **Install Playwright Browsers**:
   ```bash
   playwright install chromium
   ```

## Usage

### Basic Usage

Run the scraper with default settings (headless mode):

```bash
uv run wmoov-scraper
```

### Options

- **Debug Mode** (show browser window):
  ```bash
  uv run wmoov-scraper --no-headless
  ```

- **Verbose Logging**:
  ```bash
  uv run wmoov-scraper --verbose
  ```

### Direct Execution

Alternatively, run directly with Python:

```bash
python -m wmoov_scraper.main
```

## Output Format

The scraper outputs movie information in a clean, formatted table:

```
🎬 Weekend Movies - WMOOV
┌───────────────────────────┬──────────┬─────────────────────┬─────────────────────────┬─────────────────────────────┬──────────────┐
│ Movie Title               │ Rating   │ Genres              │ Cinemas                 │ Showtimes                   │ Price Range  │
├───────────────────────────┼──────────┼─────────────────────┼─────────────────────────┼─────────────────────────────┼──────────────┤
│ 「鬼滅之刃」無限城篇      │ 9.1      │ 動畫,動作,奇幻      │ 百老匯 MOViE MOViE      │ 百老匯 MOViE MOViE: 07:30   │ $120-130     │
│                           │          │                     │ Cinema City             │                             │              │
│ 東極島                    │ 6.2      │ 劇情                │                         │                             │ $100-110     │
└───────────────────────────┴──────────┴─────────────────────┴─────────────────────────┴─────────────────────────────┴──────────────┘

📊 Summary
┌─────────────────────────────────────────────────────────────────┐
│ 📅 Weekend: 2025-08-30 to 2025-08-31                            │
│ 🎭 Total Movies: 2                                              │
│ ⏰ Total Showtimes: 5                                           │
│ 🕒 Scraped: 2025-08-28 10:30                                    │
└─────────────────────────────────────────────────────────────────┘
```

## Project Structure

```
wmoov_scraper/
├── __init__.py
├── main.py              # Application entry point
├── scraper.py           # Core scraping logic
├── models.py            # Data models and structures
├── processor.py         # Data processing and formatting
├── date_utils.py        # Date calculation utilities
└── pyproject.toml       # Project configuration
```

## Dependencies

- **playwright**: Browser automation for reliable scraping
- **rich**: Terminal formatting and tables
- **typer**: Command-line interface framework
- **python-dateutil**: Date manipulation utilities

## Error Handling

The scraper includes robust error handling for:

- Network timeouts and connectivity issues
- Missing or changed page elements
- Data parsing failures
- Browser automation errors

Errors are logged with clear messages, and the application exits gracefully.

## Date Calculation

Automatically determines the upcoming weekend:

- **Definition**: Saturday and Sunday
- **Logic**: Calculates the next Saturday from the current date
- **Example**: If today is Thursday, targets the following Saturday and Sunday

## Requirements

- Python 3.9+
- UV package manager
- Active internet connection
- Access to WMOOV website

## Development

### Running Tests

```bash
uv run pytest
```

### Code Quality

Format code:
```bash
uv run black .
```

Lint code:
```bash
uv run ruff check .
```

## License

This project is licensed under the MIT License. Intended for educational and personal use only. Always respect WMOOV's terms of service and robots.txt.
