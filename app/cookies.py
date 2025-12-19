"""
Cookie Management Module.
Saves and loads cookies to avoid repeated logins.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional


COOKIES_FILE = "olx_cookies.json"
COOKIE_MAX_AGE_DAYS = 7  # Cookies valid for 7 days


def save_cookies(cookies: List[Dict], filepath: str = COOKIES_FILE) -> None:
    """
    Save cookies to a JSON file.
    
    Args:
        cookies: List of cookie dictionaries from Selenium
        filepath: Path to save cookies
    """
    data = {
        "saved_at": datetime.now().isoformat(),
        "cookies": cookies,
    }
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def load_cookies(filepath: str = COOKIES_FILE) -> Optional[List[Dict]]:
    """
    Load cookies from a JSON file if they exist and are not expired.
    
    Args:
        filepath: Path to cookie file
        
    Returns:
        List of cookie dictionaries or None if not valid
    """
    if not os.path.exists(filepath):
        return None
    
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Check if cookies are expired
        saved_at = datetime.fromisoformat(data.get("saved_at", "2000-01-01"))
        max_age = timedelta(days=COOKIE_MAX_AGE_DAYS)
        
        if datetime.now() - saved_at > max_age:
            # Cookies expired, delete file
            os.remove(filepath)
            return None
        
        cookies = data.get("cookies", [])
        if not cookies:
            return None
        
        return cookies
        
    except Exception:
        return None


def delete_cookies(filepath: str = COOKIES_FILE) -> None:
    """Delete saved cookies."""
    if os.path.exists(filepath):
        os.remove(filepath)


def apply_cookies_to_driver(driver, cookies: List[Dict]) -> bool:
    """
    Apply saved cookies to a Selenium WebDriver.
    
    Args:
        driver: Selenium WebDriver
        cookies: List of cookie dictionaries
        
    Returns:
        True if cookies were applied successfully
    """
    try:
        # First navigate to the domain
        driver.get("https://www.olx.com.pk/")
        
        # Clear existing cookies
        driver.delete_all_cookies()
        
        # Add saved cookies
        for cookie in cookies:
            # Remove problematic fields
            clean_cookie = {
                "name": cookie.get("name"),
                "value": cookie.get("value"),
                "domain": cookie.get("domain", ".olx.com.pk"),
                "path": cookie.get("path", "/"),
            }
            
            # Only add if name and value exist
            if clean_cookie["name"] and clean_cookie["value"]:
                try:
                    driver.add_cookie(clean_cookie)
                except Exception:
                    pass
        
        # Refresh to apply cookies
        driver.refresh()
        return True
        
    except Exception:
        return False


def get_cookies_from_driver(driver) -> List[Dict]:
    """
    Extract all cookies from a Selenium WebDriver.
    
    Args:
        driver: Selenium WebDriver
        
    Returns:
        List of cookie dictionaries
    """
    try:
        return driver.get_cookies()
    except Exception:
        return []
