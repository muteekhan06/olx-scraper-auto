"""
OLX Contact Information Fetcher.
Fetches seller contact details via authenticated API calls.
Now with cookie persistence - login only once!
"""

import json
import os
import random
import re
import time
from datetime import date
from typing import Callable, Dict, List, Optional, Tuple

import requests

from app.config import SCRAPER_CONFIG, OUTPUT_CONFIG
from app.driver import build_driver
from app.cookies import (
    save_cookies, load_cookies, delete_cookies,
    apply_cookies_to_driver, get_cookies_from_driver
)


HOME_URL = "https://www.olx.com.pk/"
API_CONTACT_FMT = "https://www.olx.com.pk/api/listing/{ad_id}/contactInfo/"


def _human_sleep(min_s: float, max_s: float) -> None:
    """Sleep for a random human-like duration."""
    time.sleep(random.uniform(min_s, max_s))


def _light_browsing(driver) -> None:
    """Simulate light human browsing behavior."""
    try:
        driver.get(HOME_URL)
    except Exception:
        return
    
    _human_sleep(0.8, 1.5)
    
    for _ in range(random.randint(1, 2)):
        try:
            driver.execute_script("window.scrollBy(0, arguments[0]);", random.randint(100, 400))
        except Exception:
            pass
        _human_sleep(0.4, 0.8)
    
    try:
        driver.execute_script("window.scrollTo(0, 0);")
    except Exception:
        pass
    
    _human_sleep(0.3, 0.6)


def _has_auth_cookies(driver) -> bool:
    """Check if authentication cookies are present."""
    try:
        cookies = {c.get("name"): c.get("value") for c in driver.get_cookies()}
    except Exception:
        return False
    
    token_keys = {"kc_access_token", "kc_refresh_token", "kc_id_token", "hb-session-id"}
    return any(k in cookies and bool(cookies.get(k)) for k in token_keys)


def _has_auth_in_cookies_list(cookies: List[Dict]) -> bool:
    """Check if authentication cookies are present in a cookie list."""
    cookie_dict = {c.get("name"): c.get("value") for c in cookies}
    token_keys = {"kc_access_token", "kc_refresh_token", "kc_id_token", "hb-session-id"}
    return any(k in cookie_dict and bool(cookie_dict.get(k)) for k in token_keys)


def _wait_for_login(driver, max_wait_s: int, progress_callback: Optional[Callable] = None) -> None:
    """Wait for user to manually log in."""
    start = time.time()
    
    try:
        driver.get(HOME_URL)
    except Exception:
        pass
    
    _human_sleep(0.8, 1.5)
    
    while time.time() - start < max_wait_s:
        if _has_auth_cookies(driver):
            if progress_callback:
                progress_callback("Login detected! Saving cookies for next time...")
            
            # Save cookies for future use
            cookies = get_cookies_from_driver(driver)
            save_cookies(cookies)
            
            return
        
        _light_browsing(driver)
        _human_sleep(0.8, 1.5)
        
        remaining = int(max_wait_s - (time.time() - start))
        if remaining % 30 == 0 and progress_callback:
            progress_callback(f"Waiting for login... {remaining}s remaining")
    
    raise TimeoutError("Login not detected within the allotted time. Please sign in and retry.")


def _transfer_cookies(driver) -> requests.Session:
    """Transfer browser cookies to a requests Session."""
    sess = requests.Session()
    
    sess.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/131.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json",
        "Accept-Language": "en,en-US;q=0.9",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": HOME_URL,
    })
    
    try:
        for c in driver.get_cookies():
            name = c.get("name")
            value = c.get("value")
            if not name or value is None:
                continue
            domain = c.get("domain") or ".olx.com.pk"
            path = c.get("path") or "/"
            sess.cookies.set(name, value, domain=domain, path=path)
    except Exception:
        pass
    
    return sess


def _transfer_cookies_from_list(cookies: List[Dict]) -> requests.Session:
    """Transfer cookie list to a requests Session."""
    sess = requests.Session()
    
    sess.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/131.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json",
        "Accept-Language": "en,en-US;q=0.9",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": HOME_URL,
    })
    
    for c in cookies:
        name = c.get("name")
        value = c.get("value")
        if not name or value is None:
            continue
        domain = c.get("domain") or ".olx.com.pk"
        path = c.get("path") or "/"
        sess.cookies.set(name, value, domain=domain, path=path)
    
    return sess


def _load_ad_ids(listings: List[Dict]) -> List[str]:
    """Extract unique Ad IDs from listings."""
    ad_ids: List[str] = []
    seen: set = set()
    
    for item in listings:
        ad = item.get("Ad ID") or item.get("ad_id") or item.get("id")
        
        if not ad:
            link = str(item.get("Link", ""))
            m = re.search(r"iid-(\d+)", link)
            if m:
                ad = m.group(1)
        
        if ad and ad not in seen:
            seen.add(ad)
            ad_ids.append(str(ad))
    
    return ad_ids


def _fetch_contact(
    sess: requests.Session,
    ad_id: str,
    referer: Optional[str] = None,
) -> Tuple[Optional[Dict], Optional[str]]:
    """Fetch contact info for a single ad."""
    url = API_CONTACT_FMT.format(ad_id=ad_id)
    headers = {}
    if referer:
        headers["Referer"] = referer
    
    try:
        resp = sess.get(url, headers=headers, timeout=20)
        if resp.status_code == 304:
            return {"status": "not_modified", "ad_id": ad_id}, None
        if resp.status_code == 200:
            return resp.json(), None
        return None, f"HTTP {resp.status_code}"
    except Exception as e:
        return None, str(e)


def _test_saved_cookies(cookies: List[Dict], progress_callback: Optional[Callable] = None) -> bool:
    """Test if saved cookies are still valid by making a test API call."""
    if not cookies or not _has_auth_in_cookies_list(cookies):
        return False
    
    sess = _transfer_cookies_from_list(cookies)
    
    # Try a simple API call to verify cookies work
    try:
        resp = sess.get("https://www.olx.com.pk/api/user/", timeout=10)
        if resp.status_code in (200, 304):
            if progress_callback:
                progress_callback("✅ Using saved login session (no login needed!)")
            return True
        elif resp.status_code in (401, 403):
            if progress_callback:
                progress_callback("Saved session expired, need fresh login...")
            return False
    except Exception:
        pass
    
    return False


def fetch_contacts(
    listings: List[Dict],
    progress_callback: Optional[Callable] = None,
) -> List[Dict]:
    """
    Fetch contact information for listings.
    Uses saved cookies if available - login only needed once!
    
    Args:
        listings: List of listing dictionaries with Ad IDs
        progress_callback: Optional callback for progress updates
        
    Returns:
        List of listings enriched with contact information
    """
    ad_ids = _load_ad_ids(listings)
    
    if not ad_ids:
        if progress_callback:
            progress_callback("No Ad IDs found in listings.")
        return listings
    
    if progress_callback:
        progress_callback(f"Found {len(ad_ids)} ads to fetch contacts for...")
    
    # Create ID to listing mapping
    id_to_listing: Dict[str, Dict] = {}
    for item in listings:
        ad = item.get("Ad ID") or item.get("ad_id")
        if not ad:
            link = str(item.get("Link", ""))
            m = re.search(r"iid-(\d+)", link)
            if m:
                ad = m.group(1)
        if ad:
            id_to_listing[str(ad)] = item
    
    # Try to use saved cookies first
    saved_cookies = load_cookies()
    driver = None
    sess = None
    
    if saved_cookies and _test_saved_cookies(saved_cookies, progress_callback):
        # Use saved cookies - no browser needed!
        sess = _transfer_cookies_from_list(saved_cookies)
    else:
        # Need fresh login
        if progress_callback:
            progress_callback("Opening browser for OLX login...")
        
        driver = build_driver(headless=False)  # Visible for login
        
        try:
            if progress_callback:
                progress_callback("Please log in to OLX in the browser window...")
            
            _wait_for_login(driver, SCRAPER_CONFIG.LOGIN_TIMEOUT, progress_callback)
            
            if progress_callback:
                progress_callback("Preparing API session...")
            
            sess = _transfer_cookies(driver)
            _light_browsing(driver)
            
        except Exception as e:
            if driver:
                try:
                    driver.quit()
                except Exception:
                    pass
            raise e
    
    # Fetch contacts
    successes = 0
    failures = 0
    
    for i, ad_id in enumerate(ad_ids, 1):
        referer = f"https://www.olx.com.pk/item/iid-{ad_id}"
        
        # Retry logic
        data = None
        last_err = None
        
        for attempt in range(3):
            data, err = _fetch_contact(sess, ad_id, referer=referer)
            
            if err is None and data is not None:
                break
            
            last_err = err
            
            if err and ("HTTP 401" in err or "HTTP 403" in err or "HTTP 429" in err):
                if "HTTP 429" in err:
                    if progress_callback:
                        progress_callback(f"Rate limited at ad {i}. Pausing...")
                    time.sleep(5)
                
                # If we have a driver, refresh cookies
                if driver:
                    try:
                        sess = _transfer_cookies(driver)
                    except Exception:
                        pass
                else:
                    # Cookies might be expired, delete and require fresh login next time
                    delete_cookies()
            
            time.sleep(1.2 * (attempt + 1))
        
        if data is None:
            failures += 1
            if progress_callback and failures <= 3:
                progress_callback(f"Failed to fetch contact for {ad_id}: {last_err}")
        else:
            successes += 1
            
            # Merge contact data into listing (exclude unwanted fields)
            if ad_id in id_to_listing and isinstance(data, dict):
                listing = id_to_listing[ad_id]
                for k, v in data.items():
                    if k not in OUTPUT_CONFIG.EXCLUDED_COLUMNS and k not in listing:
                        listing[k] = v
        
        # Polite delay
        if i % SCRAPER_CONFIG.LONG_PAUSE_FREQUENCY == 0:
            _human_sleep(SCRAPER_CONFIG.LONG_PAUSE_MIN, SCRAPER_CONFIG.LONG_PAUSE_MAX)
        else:
            _human_sleep(SCRAPER_CONFIG.MIN_REQUEST_DELAY, SCRAPER_CONFIG.MAX_REQUEST_DELAY)
        
        if progress_callback and i % 10 == 0:
            progress_callback(f"Fetched contacts: {i}/{len(ad_ids)} ({successes} success, {failures} failed)")
        
        # Occasional light browsing (only if driver is active)
        if driver and i % random.randint(8, 12) == 0:
            _light_browsing(driver)
    
    # Close driver if it was opened
    if driver:
        try:
            driver.quit()
        except Exception:
            pass
    
    if progress_callback:
        progress_callback(f"Contact fetching complete. Success: {successes}, Failed: {failures}")
    
    return listings
