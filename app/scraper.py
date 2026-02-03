"""
OLX Listing Scraper - Optimized for speed and safety.
Scrapes car listings from OLX Pakistan Lahore.
"""

import json
import random
import re
import time
from typing import Any, Callable, Dict, List, Optional, Set

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, WebDriverException

from app.config import SCRAPER_CONFIG, OUTPUT_CONFIG
from app.driver import build_driver


def sleep_jitter(min_s: float = None, max_s: float = None) -> None:
    """Sleep for a random duration within configured range."""
    min_s = min_s or SCRAPER_CONFIG.MIN_JITTER
    max_s = max_s or SCRAPER_CONFIG.MAX_JITTER
    time.sleep(random.uniform(min_s, max_s))


def scroll_page(driver: webdriver.Chrome, steps: int = 3) -> None:
    """Scroll page to load dynamic content."""
    for _ in range(steps):
        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        except Exception:
            pass
        time.sleep(SCRAPER_CONFIG.SCROLL_PAUSE)


def safe_text(element) -> str:
    """Safely extract text from a Selenium element."""
    try:
        return (element.text or "").strip()
    except Exception:
        return ""


# XPath selectors for list page
CARD_ANCESTOR_XPATH = (
    ".//ancestor::div[@aria-label='Ad']"
    " | .//ancestor::div[@data-cy='l-card']"
    " | .//ancestor::div[contains(@class,'_70cdfb32')]"
    " | .//ancestor::div[contains(@class,'_63a946ba')]"
    " | .//ancestor::article"
)

PRICE_XPATH = (
    ".//*[@aria-label='Price']//*[self::span or self::div]"
    " | .//span[contains(@class,'ddc1b288')]"
)

LOCATION_XPATH = (
    ".//*[@aria-label='Location']//*[self::span or self::div]"
    " | .//div[contains(@class,'f7d5e47e')]"
)

TITLE_FALLBACK_XPATH = (
    ".//*[@aria-label='Title']//*[self::h1 or self::h2 or self::span or self::div]"
    " | .//*[contains(@class,'_34bc0d5f')]//*[self::h1 or self::h2 or self::span or self::div]"
    " | .//*[contains(@class,'_562a2db2')]"
)


def scrape_list_page(
    driver: webdriver.Chrome,
    url: str,
    max_items: Optional[int] = None,
    progress_callback: Optional[Callable] = None,
    max_retries: int = 3,
) -> List[Dict[str, str]]:
    """
    Scrape a single list page for basic listing info.
    
    Args:
        driver: WebDriver instance
        url: Page URL to scrape
        max_items: Maximum items to collect from this page
        progress_callback: Optional callback for progress updates
        max_retries: Number of retry attempts for network errors
        
    Returns:
        List of dictionaries with basic listing data
    """
    if progress_callback:
        progress_callback(f"Loading: {url}")
    
    # Retry logic for network errors
    last_error = None
    for attempt in range(max_retries):
        try:
            driver.get(url)
            break
        except WebDriverException as e:
            last_error = e
            error_msg = str(e)
            if "ERR_NAME_NOT_RESOLVED" in error_msg or "ERR_INTERNET_DISCONNECTED" in error_msg or "ERR_CONNECTION" in error_msg:
                if progress_callback:
                    progress_callback(f"Network error (attempt {attempt + 1}/{max_retries}): Retrying in 5s...")
                time.sleep(5)
            else:
                raise
    else:
        if progress_callback:
            progress_callback(f"Failed to connect after {max_retries} attempts: {last_error}")
        return []
    
    try:
        WebDriverWait(driver, SCRAPER_CONFIG.PAGE_WAIT).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href*="/item/"][href*="iid-"]'))
        )
    except TimeoutException:
        if progress_callback:
            progress_callback("No listings found on page (timeout)")
        return []
    
    scroll_page(driver)
    
    anchors = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/item/"][href*="iid-"]')
    seen: Set[str] = set()
    links: List[tuple] = []
    
    for anchor in anchors:
        try:
            href = anchor.get_attribute("href") or ""
            if "/item/" in href and "iid-" in href and href not in seen:
                seen.add(href)
                links.append((anchor, href))
        except StaleElementReferenceException:
            continue
    
    if progress_callback:
        progress_callback(f"Found {len(links)} listings")
    
    rows: List[Dict[str, str]] = []
    take = links[: (max_items or len(links))]
    
    for anchor, href in take:
        try:
            card = anchor.find_element(By.XPATH, CARD_ANCESTOR_XPATH)
        except Exception:
            card = None
        
        # Extract title
        title = ""
        try:
            title = (anchor.get_attribute("title") or "").strip()
        except Exception:
            pass
        
        if not title and card:
            try:
                t_el = card.find_element(By.XPATH, TITLE_FALLBACK_XPATH)
                title = safe_text(t_el)
            except Exception:
                pass
        
        # Extract price
        price = ""
        if card:
            try:
                p_el = card.find_element(By.XPATH, PRICE_XPATH)
                price = safe_text(p_el)
            except Exception:
                pass
        
        # Extract location
        location = ""
        if card:
            try:
                l_el = card.find_element(By.XPATH, LOCATION_XPATH)
                location = safe_text(l_el)
            except Exception:
                pass
        
        rows.append({
            "Title": title,
            "Link": href,
            "Price": price,
            "Location": location,
        })
    
    return rows


def parse_json_ld(soup: BeautifulSoup) -> Dict[str, str]:
    """Extract structured data from JSON-LD scripts."""
    out: Dict[str, str] = {}
    images: List[str] = []
    
    for script in soup.find_all("script", {"type": "application/ld+json"}):
        try:
            raw = script.string or script.get_text() or ""
            if not raw.strip():
                continue
            obj = json.loads(raw)
        except Exception:
            continue
        
        objs = obj if isinstance(obj, list) else [obj]
        for o in objs:
            if not isinstance(o, dict):
                continue
            
            at = o.get("@type", "")
            types = set(at) if isinstance(at, list) else {at}
            if not (types & {"Product", "Offer", "Vehicle", "Car", "WebPage", "Organization"}):
                continue
            
            name = o.get("name") or o.get("headline")
            if name and not out.get("Title"):
                out["Title"] = str(name).strip()
            
            desc = o.get("description")
            if desc and not out.get("Description"):
                out["Description"] = str(desc).strip()
            
            img = o.get("image")
            if isinstance(img, list):
                images.extend([str(i) for i in img if isinstance(i, str)])
            elif isinstance(img, str):
                images.append(img)
            
            offers = o.get("offers")
            if isinstance(offers, dict):
                price = offers.get("price")
                curr = offers.get("priceCurrency")
                if price and not out.get("Price"):
                    out["Price"] = f"{curr or ''} {price}".strip()
            
            seller = o.get("seller")
            if isinstance(seller, dict):
                sname = seller.get("name")
                if sname and not out.get("Seller Name"):
                    out["Seller Name"] = str(sname).strip()
    
    if images:
        out["Images"] = ", ".join(sorted(set(images)))
    
    return out


def extract_text(soup: BeautifulSoup, selectors: List[str]) -> str:
    """Extract text using multiple CSS selector fallbacks."""
    for sel in selectors:
        el = soup.select_one(sel)
        if el:
            t = el.get_text(strip=True)
            if t:
                return t
    return ""


def extract_specs(soup: BeautifulSoup) -> Dict[str, str]:
    """Extract specifications from list/definition elements."""
    specs: Dict[str, str] = {}
    
    for li in soup.select("ul li, .ad-attributes li"):
        texts = [t.get_text(strip=True) for t in li.find_all(["span", "div"]) if t.get_text(strip=True)]
        if len(texts) >= 2:
            k = re.sub(r"[\s\-:/]+", "_", texts[0].strip()).lower()
            v = " ".join(texts[1:])
            if k and v:
                specs[k] = v
    
    for dl in soup.select("dl"):
        dts = dl.find_all("dt")
        dds = dl.find_all("dd")
        for dt, dd in zip(dts, dds):
            k = re.sub(r"[\s\-:/]+", "_", dt.get_text(strip=True)).lower()
            v = dd.get_text(strip=True)
            if k and v:
                specs[k] = v
    
    return specs


def extract_images(soup: BeautifulSoup) -> str:
    """Extract all image URLs from the page."""
    urls: Set[str] = set()
    
    for img in soup.find_all("img"):
        src = (img.get("src") or "").strip()
        if src.startswith("http"):
            urls.add(src)
        dsrc = (img.get("data-src") or "").strip()
        if dsrc.startswith("http"):
            urls.add(dsrc)
        srcset = (img.get("srcset") or "").strip()
        if srcset:
            for token in srcset.split(","):
                url = token.strip().split(" ")[0]
                if url.startswith("http"):
                    urls.add(url)
    
    for source in soup.find_all("source"):
        srcset = (source.get("srcset") or "").strip()
        if srcset:
            for token in srcset.split(","):
                url = token.strip().split(" ")[0]
                if url.startswith("http"):
                    urls.add(url)
    
    return ", ".join(sorted(urls))


def extract_ad_id(soup: BeautifulSoup) -> str:
    """Extract Ad ID from the page."""
    node = soup.find(attrs={"data-aut-id": "adId"})
    if node:
        return node.get_text(strip=True).replace("Ad ID", "").replace(":", "").strip()
    
    m = re.search(r"Ad\s*ID\s*:\s*(\w+)", soup.get_text(" ", strip=True), flags=re.I)
    return m.group(1).strip() if m else ""


def extract_detail(driver: webdriver.Chrome, url: str, max_retries: int = 3) -> Dict[str, str]:
    """
    Extract detailed information from a listing page.
    
    Args:
        driver: WebDriver instance
        url: Listing page URL
        max_retries: Number of retry attempts for network errors
        
    Returns:
        Dictionary with detailed listing data
    """
    d: Dict[str, str] = {"Link": url}
    
    # Retry logic for network errors
    for attempt in range(max_retries):
        try:
            driver.get(url)
            break
        except WebDriverException as e:
            error_msg = str(e)
            if "ERR_NAME_NOT_RESOLVED" in error_msg or "ERR_INTERNET_DISCONNECTED" in error_msg or "ERR_CONNECTION" in error_msg:
                if attempt < max_retries - 1:
                    time.sleep(3)
                    continue
            raise
    
    try:
        WebDriverWait(driver, SCRAPER_CONFIG.DETAIL_WAIT).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
    except TimeoutException:
        return d  # Return minimal data on timeout
    
    sleep_jitter(0.3, 0.6)
    scroll_page(driver, steps=2)
    
    soup = BeautifulSoup(driver.page_source, "html.parser")
    d.update(parse_json_ld(soup))
    
    # Title
    d.setdefault("Title", extract_text(soup, [
        "h1", "[data-testid='ad-title']", "h1._562a2db2", "h1[itemprop='name']"
    ]))
    
    # Price
    d.setdefault("Price", extract_text(soup, [
        "[aria-label='Price'] span", "[data-testid='ad-price']",
        "span.ddc1b288", ".price", "[itemprop='price']"
    ]))
    
    # Description
    if not d.get("Description"):
        desc = extract_text(soup, [
            "[data-aut-id='itemDescriptionContent']", "[data-testid='ad-description']",
            "#description", ".description", "[itemprop='description']"
        ])
        if not desc:
            node = soup.select_one(
                "[data-aut-id='itemDescriptionContent'], [data-testid='ad-description'], "
                "#description, .description, [itemprop='description']"
            )
            if node:
                parts = [x.get_text(strip=True) for x in node.find_all(["p", "span", "div"]) if x.get_text(strip=True)]
                desc = " ".join(parts) if parts else node.get_text(strip=True)
        d["Description"] = desc or ""
    
    # Images
    d.setdefault("Images", extract_images(soup))
    
    # Location
    d["Location"] = d.get("Location") or extract_text(soup, [
        '[data-aut-id="item-location"]', ".seller-location",
        '[aria-label="Location"]', "div.f7d5e47e"
    ])
    
    
    # Seller info
    seller_name = extract_text(soup, ['[data-testid="seller-name"]', '[data-aut-id="profileCard"] h4'])
    if seller_name:
        d["Seller Name"] = seller_name
    
    # Seller Since - More robust extraction
    seller_since = extract_text(soup, [
        ".seller-since", 
        '[data-aut-id="sub-title"]', 
        '[aria-label="Member since"]', 
        'div._053301d8'
    ])
    
    if not seller_since:
        # Try to find "Member since" text globally in the profile card
        card_text = extract_text(soup, ['[data-aut-id="profileCard"]', 'div[class*="profile-card"]'])
        m = re.search(r"Member since\s+([A-Za-z]+\s+\d{4})", card_text, re.I)
        if m:
            seller_since = m.group(1)
            
    d["Seller Since"] = seller_since or ""
    
    # Ad ID
    d["Ad ID"] = d.get("Ad ID") or extract_ad_id(soup)
    
    # Seller profile
    prof = soup.select_one('a[href*="/profile/"]')
    if prof and not d.get("seller_profile"):
        href = prof.get("href") or ""
        if href:
            d["seller_profile"] = href if href.startswith("http") else f"https://www.olx.com.pk{href}"
    
    # Specs
    specs = extract_specs(soup)
    for k, v in specs.items():
        if v and k not in OUTPUT_CONFIG.EXCLUDED_COLUMNS and not d.get(k):
            d[k] = v
    
    # Clean output - remove excluded columns
    clean: Dict[str, str] = {}
    for k, v in d.items():
        if k in OUTPUT_CONFIG.EXCLUDED_COLUMNS:
            continue
        if v is None:
            clean[k] = ""
        elif isinstance(v, str) and v.strip().upper() == "N/A":
            clean[k] = ""
        else:
            clean[k] = v.strip() if isinstance(v, str) else str(v)
    
    return clean


def scrape_listings(
    max_pages: int = None,
    max_listings: int = None,
    progress_callback: Optional[Callable] = None,
    selected_locations: Optional[List[str]] = None,
) -> List[Dict[str, str]]:
    """
    Main scraping function - collects listings from multiple Lahore locations.
    
    Args:
        max_pages: Maximum pages to scrape per location
        max_listings: Maximum total listings to collect per location
        progress_callback: Optional callback for progress updates
        selected_locations: List of location keys to scrape (e.g., ['johar_town', 'model_town'])
                           If None, scrapes from all enabled locations
        
    Returns:
        List of dictionaries with listing data from all locations
    """
    max_pages = max_pages or SCRAPER_CONFIG.DEFAULT_MAX_PAGES
    max_listings_per_location = SCRAPER_CONFIG.LISTINGS_PER_LOCATION
    
    # Determine which locations to scrape
    if selected_locations is None:
        # Scrape all enabled locations
        locations_to_scrape = {
            key: loc for key, loc in SCRAPER_CONFIG.LOCATIONS.items() 
            if loc.get("enabled", True)
        }
    else:
        # Scrape only selected locations
        locations_to_scrape = {
            key: SCRAPER_CONFIG.LOCATIONS[key] 
            for key in selected_locations 
            if key in SCRAPER_CONFIG.LOCATIONS
        }
    
    if not locations_to_scrape:
        if progress_callback:
            progress_callback("No locations selected for scraping.")
        return []
    
    if progress_callback:
        location_names = [loc["name"] for loc in locations_to_scrape.values()]
        progress_callback(f"Starting scrape for {len(locations_to_scrape)} location(s): {', '.join(location_names)}")
    
    all_results: List[Dict[str, str]] = []
    
    # Scrape each location sequentially for safety and reliability
    def scrape_single_location(location_key: str, location_info: dict) -> List[Dict[str, str]]:
        location_name = location_info["name"]
        base_url = location_info["url"]
        
        if progress_callback:
            progress_callback(f"📍 {location_name}: Starting scrape (target: {max_listings_per_location} listings)...")
        
        master_driver = build_driver(headless=True)
        all_basics: List[Dict[str, str]] = []
        
        try:
            # Phase 1: Collect listing links for this location
            for page in range(1, max_pages + 1):
                url = base_url if page == 1 else f"{base_url}?page={page}"
                
                if progress_callback:
                    progress_callback(f"📍 {location_name}: Page {page}/{max_pages}...")
                
                basics = scrape_list_page(master_driver, url, max_items=24, progress_callback=progress_callback)
                
                if not basics:
                    if progress_callback:
                        progress_callback(f"📍 {location_name}: No items on page {page}, stopping.")
                    break
                
                all_basics.extend(basics)
                
                if len(all_basics) >= max_listings_per_location:
                    all_basics = all_basics[:max_listings_per_location]
                    if progress_callback:
                        progress_callback(f"📍 {location_name}: Reached target of {max_listings_per_location} listings.")
                    break
                
                sleep_jitter(SCRAPER_CONFIG.MIN_REQUEST_DELAY, SCRAPER_CONFIG.MAX_REQUEST_DELAY)
        
        finally:
            try:
                master_driver.quit()
            except Exception:
                pass
        
        if not all_basics:
            if progress_callback:
                progress_callback(f"📍 {location_name}: No listings found.")
            return []
        
        if progress_callback:
            progress_callback(f"📍 {location_name}: Collected {len(all_basics)} listings. Fetching details...")
        
        # Phase 2: Scrape details sequentially for this location (safe, no conflicts)
        location_results: List[Dict[str, str]] = []
        detail_driver = build_driver(headless=True)
        
        try:
            for idx, item in enumerate(all_basics):
                try:
                    detail = extract_detail(detail_driver, item["Link"])
                except Exception as e:
                    detail = {"Link": item.get("Link", ""), "error": str(e)}
                    if progress_callback:
                        progress_callback(f"📍 {location_name}: Error on listing {idx+1}: {e}")
                
                merged = dict(detail)
                for k, v in item.items():
                    if k not in merged or (not merged[k] and v):
                        merged[k] = v or ""
                
                # Add location metadata
                merged["Scraped_Location"] = location_name
                merged["Location_Key"] = location_key
                
                location_results.append(merged)
                
                # Progress update
                if progress_callback and (idx + 1) % 5 == 0:
                    progress_callback(f"📍 {location_name}: Processed {idx + 1}/{len(all_basics)} listings...")
                
                # Polite delay
                if (idx + 1) % SCRAPER_CONFIG.LONG_PAUSE_FREQUENCY == 0:
                    sleep_jitter(SCRAPER_CONFIG.LONG_PAUSE_MIN, SCRAPER_CONFIG.LONG_PAUSE_MAX)
                else:
                    sleep_jitter(SCRAPER_CONFIG.MIN_REQUEST_DELAY, SCRAPER_CONFIG.MAX_REQUEST_DELAY)
        finally:
            try:
                detail_driver.quit()
            except Exception:
                pass
        
        if progress_callback:
            progress_callback(f"✅ {location_name}: Completed! {len(location_results)} listings scraped.")
        
        return location_results
    
    # Scrape locations sequentially (safe, no WebDriver conflicts)
    for location_key, location_info in locations_to_scrape.items():
        try:
            location_results = scrape_single_location(location_key, location_info)
            all_results.extend(location_results)
        except Exception as e:
            location_name = location_info["name"]
            if progress_callback:
                progress_callback(f"❌ {location_name}: Error - {e}")
    
    if progress_callback:
        progress_callback(f"🎉 All locations complete! Total: {len(all_results)} listings from {len(locations_to_scrape)} location(s).")
    
    return all_results
