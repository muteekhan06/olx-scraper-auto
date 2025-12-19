"""
Configuration settings for OLX Scraper.
Centralized config for easy tuning and maintenance.
"""

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class ScraperConfig:
    """Scraper timing and behavior configuration."""
    
    # Base URL for Lahore cars
    BASE_URL: str = "https://www.olx.com.pk/lahore_g4060673/cars_c84"
    
    # Page load timeouts (seconds) - reduced for speed
    PAGE_WAIT: int = 10
    DETAIL_WAIT: int = 8
    
    # Optimized delays (faster but still human-like)
    MIN_JITTER: float = 0.2
    MAX_JITTER: float = 0.6
    SCROLL_PAUSE: float = 0.3
    
    # Between-request delays - fast but varied to look human
    MIN_REQUEST_DELAY: float = 0.3
    MAX_REQUEST_DELAY: float = 0.8
    LONG_PAUSE_MIN: float = 1.5
    LONG_PAUSE_MAX: float = 2.5
    LONG_PAUSE_FREQUENCY: int = 10  # Every N requests take longer pause
    
    # Concurrency - more workers = faster
    DETAIL_WORKERS: int = 3  # Parallel detail page fetchers
    
    # Login timeout for contact fetching
    LOGIN_TIMEOUT: int = 240
    
    # Default scraping limits
    DEFAULT_MAX_PAGES: int = 5
    DEFAULT_MAX_LISTINGS: int = 50


@dataclass(frozen=True)
class OutputConfig:
    """Output file configuration."""
    
    # Output directories
    OUTPUT_DIR: str = "output"
    CONTACT_DIR: str = "contact_info"
    LISTING_DETAILS_DIR: str = "listing_details"
    
    # Columns to EXCLUDE from final output
    EXCLUDED_COLUMNS: tuple = (
        "Breadcrumb Path",
        "Posted",
        "chat_available",
        "call_available",
        "Thumbnail Image",
        "proxyMobile",
        "roles",
    )
    
    # Preferred column order for TSV output
    COLUMN_ORDER: tuple = (
        "Ad ID",
        "Title",
        "Price",
        "Location",
        "Description",
        "Link",
        "Images",
        "Seller Name",
        "Seller Since",
        "seller_profile",
        "name",
        "mobile",
        "whatsapp",
        "mobileNumbers",
    )
    
    # Default Google Sheet ID - Replace with your own spreadsheet ID
    # Find it in your sheet URL: docs.google.com/spreadsheets/d/[THIS-IS-YOUR-ID]/edit
    GOOGLE_SHEET_ID: str = ""


# Global instances
SCRAPER_CONFIG = ScraperConfig()
OUTPUT_CONFIG = OutputConfig()
