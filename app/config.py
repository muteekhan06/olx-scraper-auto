"""
Configuration settings for OLXify.
Centralized config for easy tuning and maintenance.
"""

import os
from dataclasses import dataclass
from typing import List


# Project root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
CONFIG_DIR = os.path.join(PROJECT_ROOT, "config")


# Load environment variables from config/.env file
def _load_env():
    env_path = os.path.join(CONFIG_DIR, ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ.setdefault(key.strip(), value.strip())

_load_env()


@dataclass(frozen=True)
class ScraperConfig:
    """Scraper timing and behavior configuration."""
    
    # Multi-location configuration for Lahore areas
    LOCATIONS: dict = None  # Will be set below
    
    # Page load timeouts (seconds) - optimized for speed
    PAGE_WAIT: int = 7
    DETAIL_WAIT: int = 5
    
    # Optimized delays (faster but still human-like)
    MIN_JITTER: float = 0.1
    MAX_JITTER: float = 0.3
    SCROLL_PAUSE: float = 0.2
    
    # Between-request delays - fast but varied to look human
    MIN_REQUEST_DELAY: float = 0.2
    MAX_REQUEST_DELAY: float = 0.5
    LONG_PAUSE_MIN: float = 1.0
    LONG_PAUSE_MAX: float = 1.5
    LONG_PAUSE_FREQUENCY: int = 15  # Every N requests take longer pause
    
    # Concurrency - more workers = faster (increased for parallel processing)
    DETAIL_WORKERS: int = 6  # Parallel detail page fetchers
    
    # Login timeout for contact fetching
    LOGIN_TIMEOUT: int = 240
    
    # Default scraping limits
    DEFAULT_MAX_PAGES: int = 5
    DEFAULT_MAX_LISTINGS: int = 50
    
    # Per-location listing limit (50 from each area)
    LISTINGS_PER_LOCATION: int = 50


# Define available locations for scraping
LOCATIONS_CONFIG = {
    "johar_town": {
        "name": "Johar Town",
        "url": "https://www.olx.com.pk/johar-town_g5000042/cars_c84",
        "enabled": True,
    },
    "model_town": {
        "name": "Model Town",
        "url": "https://www.olx.com.pk/model-town_g5000051/cars_c84",
        "enabled": True,
    },
    "valencia_town": {
        "name": "Valencia Town",
        "url": "https://www.olx.com.pk/valencia-town_g5000081/cars_c84",
        "enabled": True,
    },
    "askari": {
        "name": "Askari",
        "url": "https://www.olx.com.pk/askari_g5000331/cars_c84",
        "enabled": True,
    },
    "dha_defence": {
        "name": "DHA Defence",
        "url": "https://www.olx.com.pk/dha-defence_g9/cars_c84",
        "enabled": True,
    },
}


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
        "Images",
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


# Global instances
SCRAPER_CONFIG = ScraperConfig()

# Inject LOCATIONS into SCRAPER_CONFIG
object.__setattr__(SCRAPER_CONFIG, 'LOCATIONS', LOCATIONS_CONFIG)

# OutputConfig needs to be created after env is loaded
class OutputConfigWithEnv(OutputConfig):
    """OutputConfig with environment variable support."""
    GOOGLE_SHEET_ID: str = os.environ.get("GOOGLE_SHEET_ID", "")

OUTPUT_CONFIG = OutputConfigWithEnv()
