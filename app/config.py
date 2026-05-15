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
    "dha_defence": {
        "name": "DHA Defence",
        "url": "https://www.olx.com.pk/dha-defence_g9/cars_c84",
        "enabled": True,
    },
    "johar_town": {
        "name": "Johar Town",
        "url": "https://www.olx.com.pk/johar-town_g5000042/cars_c84",
        "enabled": True,
    },
    "allama_iqbal_town": {
        "name": "Allama Iqbal Town",
        "url": "https://www.olx.com.pk/allama-iqbal-town_g5000002/cars_c84",
        "enabled": True,
    },
    "gulberg": {
        "name": "Gulberg",
        "url": "https://www.olx.com.pk/gulberg_g7/cars_c84",
        "enabled": True,
    },
    "bahria_town": {
        "name": "Bahria Town",
        "url": "https://www.olx.com.pk/bahria-town_g5000005/cars_c84",
        "enabled": True,
    },
    "cantt": {
        "name": "Cantt",
        "url": "https://www.olx.com.pk/cantt_g5000047/cars_c84",
        "enabled": True,
    },
    "model_town": {
        "name": "Model Town",
        "url": "https://www.olx.com.pk/model-town_g5000051/cars_c84",
        "enabled": True,
    },
    "sabzazar": {
        "name": "Sabzazar",
        "url": "https://www.olx.com.pk/sabzazar_g5000064/cars_c84",
        "enabled": True,
    },
    "township": {
        "name": "Township",
        "url": "https://www.olx.com.pk/township_g5000078/cars_c84",
        "enabled": True,
    },
    "wapda_town": {
        "name": "Wapda Town",
        "url": "https://www.olx.com.pk/wapda-town_g5000079/cars_c84",
        "enabled": True,
    },
    "samanabad": {
        "name": "Samanabad",
        "url": "https://www.olx.com.pk/samanabad_g5000791/cars_c84",
        "enabled": True,
    },
    "faisal_town": {
        "name": "Faisal Town",
        "url": "https://www.olx.com.pk/faisal-town_g5000024/cars_c84",
        "enabled": True,
    },
    "gulshan_e_ravi": {
        "name": "Gulshan-e-Ravi",
        "url": "https://www.olx.com.pk/gulshan-e-ravi_g5000033/cars_c84",
        "enabled": True,
    },
    "gt_road": {
        "name": "GT Road",
        "url": "https://www.olx.com.pk/gt-road_g5000475/cars_c84",
        "enabled": True,
    },
    "shahdara": {
        "name": "Shahdara",
        "url": "https://www.olx.com.pk/shahdara_g5000069/cars_c84",
        "enabled": True,
    },
    "askari": {
        "name": "Askari",
        "url": "https://www.olx.com.pk/askari_g5000331/cars_c84",
        "enabled": True,
    },
    "valencia_town": {
        "name": "Valencia Town",
        "url": "https://www.olx.com.pk/valencia-town_g5000081/cars_c84",
        "enabled": True,
    },
    "raiwind_road": {
        "name": "Raiwind Road",
        "url": "https://www.olx.com.pk/raiwind-road_g5000741/cars_c84",
        "enabled": True,
    },
    "shadbagh": {
        "name": "Shadbagh",
        "url": "https://www.olx.com.pk/shadbagh_g5000068/cars_c84",
        "enabled": True,
    },
    "jail_road": {
        "name": "Jail Road",
        "url": "https://www.olx.com.pk/jail-road_g5000539/cars_c84",
        "enabled": True,
    },
    "al_rehman_garden": {
        "name": "Al Rehman Garden",
        "url": "https://www.olx.com.pk/al-rehman-garden_g5000314/cars_c84",
        "enabled": True,
    },
    "mughalpura": {
        "name": "Mughalpura",
        "url": "https://www.olx.com.pk/mughalpura_g5000055/cars_c84",
        "enabled": True,
    },
    "park_view_villas": {
        "name": "Park View Villas",
        "url": "https://www.olx.com.pk/park-view-villas_g5000709/cars_c84",
        "enabled": True,
    },
    "thokar_niaz_baig": {
        "name": "Thokar Niaz Baig",
        "url": "https://www.olx.com.pk/thokar-niaz-baig_g5000077/cars_c84",
        "enabled": True,
    },
    "bahria_orchard": {
        "name": "Bahria Orchard",
        "url": "https://www.olx.com.pk/bahria-orchard_g5000356/cars_c84",
        "enabled": True,
    },
    "baghbanpura": {
        "name": "Baghbanpura",
        "url": "https://www.olx.com.pk/baghbanpura_g5000004/cars_c84",
        "enabled": True,
    },
    "pak_arab_housing": {
        "name": "Pak Arab Housing Society",
        "url": "https://www.olx.com.pk/pak-arab-housing-society_g5000701/cars_c84",
        "enabled": True,
    },
    "marghzar_officers": {
        "name": "Marghzar Officers Colony",
        "url": "https://www.olx.com.pk/marghzar-officers-colony_g5000621/cars_c84",
        "enabled": True,
    },
    "harbanspura": {
        "name": "Harbanspura",
        "url": "https://www.olx.com.pk/harbanspura_g5000035/cars_c84",
        "enabled": True,
    },
    "central_park": {
        "name": "Central Park Housing Scheme",
        "url": "https://www.olx.com.pk/central-park-housing-scheme_g5000383/cars_c84",
        "enabled": True,
    },
    "chungi_amar_sadhu": {
        "name": "Chungi Amar Sadhu",
        "url": "https://www.olx.com.pk/chungi-amar-sadhu_g5000398/cars_c84",
        "enabled": True,
    },
    "gajju_matah": {
        "name": "Gajju Matah",
        "url": "https://www.olx.com.pk/gajju-matah_g5000450/cars_c84",
        "enabled": True,
    },
    "garden_town": {
        "name": "Garden Town",
        "url": "https://www.olx.com.pk/garden-town_g5000025/cars_c84",
        "enabled": True,
    },
    "daroghewala": {
        "name": "Daroghewala",
        "url": "https://www.olx.com.pk/daroghewala_g5000010/cars_c84",
        "enabled": True,
    },
    "ferozepur_road": {
        "name": "Ferozepur Road",
        "url": "https://www.olx.com.pk/ferozepur-road_g5000446/cars_c84",
        "enabled": True,
    },
    "tajpura": {
        "name": "Tajpura",
        "url": "https://www.olx.com.pk/tajpura_g5000074/cars_c84",
        "enabled": True,
    },
    "lda_avenue": {
        "name": "LDA Avenue",
        "url": "https://www.olx.com.pk/lda-avenue_g5000601/cars_c84",
        "enabled": True,
    },
    "walton_road": {
        "name": "Walton Road",
        "url": "https://www.olx.com.pk/walton-road_g5000883/cars_c84",
        "enabled": True,
    },
    "maulana_shaukat_ali_road": {
        "name": "Maulana Shaukat Ali Road",
        "url": "https://www.olx.com.pk/maulana-shaukat-ali-road_g5000624/cars_c84",
        "enabled": True,
    },
    "taj_bagh": {
        "name": "Taj Bagh",
        "url": "https://www.olx.com.pk/taj-bagh_g5000073/cars_c84",
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
