import json
import time
from app.driver import build_driver

def main():
    print("="*50)
    print("OLX Cookie Extractor")
    print("="*50)
    print("1. A browser will open.")
    print("2. Log in to OLX.com.pk manually.")
    print("3. Return here and press ENTER once you are logged in.")
    
    driver = build_driver(headless=False)
    driver.get("https://www.olx.com.pk")
    
    input("\nPress ENTER after you have successfully logged in...")
    
    cookies = driver.get_cookies()
    driver.quit()
    
    # Filter for important ones if needed, or just keep all
    print("\n" + "-"*50)
    print("COPY THE CONTENT BELOW THIS LINE:")
    print("-" * 50)
    print(json.dumps(cookies))
    print("-" * 50)
    print("\nPaste this into your GitHub Secret: OLX_AUTH_COOKIES")

if __name__ == "__main__":
    main()
