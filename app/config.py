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
    
    # Page load timeouts (seconds) - balanced for speed + reliability
    PAGE_WAIT: int = 5
    DETAIL_WAIT: int = 3
    
    # Delays - tuned for reliable data capture
    MIN_JITTER: float = 0.3
    MAX_JITTER: float = 0.7
    SCROLL_PAUSE: float = 0.2
    
    # Between-request delays - safe but efficient
    MIN_REQUEST_DELAY: float = 0.5
    MAX_REQUEST_DELAY: float = 1.2
    LONG_PAUSE_MIN: float = 2.0
    LONG_PAUSE_MAX: float = 3.5
    LONG_PAUSE_FREQUENCY: int = 40
    
    # Concurrency
    DETAIL_WORKERS: int = 6
    
    # Login timeout for contact fetching
    LOGIN_TIMEOUT: int = 60
    
    # Default scraping limits
    DEFAULT_MAX_PAGES: int = 2
    DEFAULT_MAX_LISTINGS: int = 15
    
    # Per-location listing limit
    LISTINGS_PER_LOCATION: int = 15


# Define available locations for scraping
# Define available locations for scraping
LOCATIONS_LAHORE = {
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
        "name": "DHA Defence (Lahore)",
        "url": "https://www.olx.com.pk/dha-defence_g9/cars_c84",
        "enabled": True,
    },
}

LOCATIONS_KARACHI = {
    "gulshan_iqbal": {
        "name": "Gulshan-e-Iqbal Town",
        "url": "https://www.olx.com.pk/gulshan-e-iqbal-town_g6858/cars_c84",
        "enabled": True,
    },
    "gulistan_jauhar": {
        "name": "Gulistan-e-Jauhar",
        "url": "https://www.olx.com.pk/gulistan-e-jauhar_g232/cars_c84",
        "enabled": True,
    },
    "fb_area": {
        "name": "Federal B Area",
        "url": "https://www.olx.com.pk/federal-b-area_g5001513/cars_c84",
        "enabled": True,
    },
    "north_nazimabad": {
        "name": "North Nazimabad",
        "url": "https://www.olx.com.pk/north-nazimabad_g5001585/cars_c84",
        "enabled": True,
    },
    "nazimabad": {
        "name": "Nazimabad",
        "url": "https://www.olx.com.pk/nazimabad_g5000215/cars_c84",
        "enabled": True,
    },
    "naya_nazimabad": {
        "name": "Naya Nazimabad",
        "url": "https://www.olx.com.pk/naya-nazimabad_g5001578/cars_c84",
        "enabled": True,
    },
    "north_karachi": {
        "name": "North Karachi",
        "url": "https://www.olx.com.pk/north-karachi_g5001584/cars_c84",
        "enabled": True,
    },
    "new_karachi": {
        "name": "New Karachi",
        "url": "https://www.olx.com.pk/new-karachi_g5001580/cars_c84",
        "enabled": True,
    },
    "saddar_town": {
        "name": "Saddar Town",
        "url": "https://www.olx.com.pk/saddar-town_g5000238/cars_c84",
        "enabled": True,
    },
    "dha_defence_karachi": {
        "name": "DHA Defence (Karachi)",
        "url": "https://www.olx.com.pk/dha-defence_g213/cars_c84",
        "enabled": True,
    },
    "clifton": {
        "name": "Clifton",
        "url": "https://www.olx.com.pk/clifton_g5000262/cars_c84",
        "enabled": True,
    },
    "buffer_zone_north": {
        "name": "North Karachi - Buffer Zone",
        "url": "https://www.olx.com.pk/north-karachi-buffer-zone_g1000000000000401/cars_c84",
        "enabled": True,
    },
    "buffer_zone_2": {
        "name": "Buffer Zone 2",
        "url": "https://www.olx.com.pk/buffer-zone-2_g5000107/cars_c84",
        "enabled": True,
    },
    "khalid_bin_walid": {
        "name": "Khalid Bin Walid Road",
        "url": "https://www.olx.com.pk/khalid-bin-walid-road_g5001552/cars_c84",
        "enabled": True,
    },
}

# Combine all locations
LOCATIONS_CONFIG = {**LOCATIONS_LAHORE, **LOCATIONS_KARACHI}


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
