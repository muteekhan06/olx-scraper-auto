"""
Chrome WebDriver management with anti-detection measures.
"""

import threading
from typing import Optional, Set

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


# Thread-local storage for per-thread drivers
_thread_local = threading.local()
_active_drivers: Set[webdriver.Chrome] = set()
_drivers_lock = threading.Lock()


def build_driver(headless: bool = True) -> webdriver.Chrome:
    """
    Create a Chrome WebDriver with anti-detection measures.
    
    Args:
        headless: Run in headless mode if True
        
    Returns:
        Configured Chrome WebDriver instance
    """
    chrome_opts = Options()
    
    if headless:
        chrome_opts.add_argument("--headless=new")
    
    # Performance and stability
    chrome_opts.add_argument("--no-sandbox")
    chrome_opts.add_argument("--disable-dev-shm-usage")
    chrome_opts.add_argument("--disable-gpu")
    chrome_opts.add_argument("--window-size=1920,1080")
    chrome_opts.add_argument("--lang=en-US")
    chrome_opts.add_argument("--disable-extensions")
    chrome_opts.add_argument("--disable-infobars")
    chrome_opts.add_argument("--disable-notifications")
    
    # Anti-detection
    chrome_opts.add_argument("--disable-blink-features=AutomationControlled")
    chrome_opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_opts.add_experimental_option("useAutomationExtension", False)
    chrome_opts.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    )
    
    try:
        driver = webdriver.Chrome(options=chrome_opts)
        
        # Mask webdriver property
        driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {"source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"}
        )
        
        with _drivers_lock:
            _active_drivers.add(driver)
        
        return driver
        
    except Exception as primary_error:
        # Fallback to undetected-chromedriver if available
        try:
            import undetected_chromedriver as uc
            
            uc_opts = uc.ChromeOptions()
            if headless:
                uc_opts.add_argument("--headless=new")
            uc_opts.add_argument("--no-sandbox")
            uc_opts.add_argument("--disable-dev-shm-usage")
            uc_opts.add_argument("--window-size=1920,1080")
            
            driver = uc.Chrome(options=uc_opts, use_subprocess=True)
            
            with _drivers_lock:
                _active_drivers.add(driver)
            
            return driver
            
        except Exception:
            raise RuntimeError(
                f"Failed to initialize Chrome WebDriver. "
                f"Ensure Google Chrome is installed. Error: {primary_error}"
            )


def get_thread_driver(headless: bool = True) -> webdriver.Chrome:
    """
    Get or create a driver for the current thread.
    
    Args:
        headless: Run in headless mode if True
        
    Returns:
        Chrome WebDriver for this thread
    """
    driver: Optional[webdriver.Chrome] = getattr(_thread_local, "driver", None)
    
    # Check if driver is still alive
    if driver is not None:
        try:
            _ = driver.current_url
            return driver
        except Exception:
            driver = None
    
    # Create new driver for this thread
    driver = build_driver(headless)
    _thread_local.driver = driver
    return driver


def cleanup_all_drivers() -> None:
    """Close all active WebDriver instances."""
    with _drivers_lock:
        for driver in list(_active_drivers):
            try:
                driver.quit()
            except Exception:
                pass
        _active_drivers.clear()
