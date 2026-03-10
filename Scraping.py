import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- Configuration ---
QUERY = "PG in sangli"
OUTPUT = "pg_data.csv"

options = Options()
# options.add_argument("--headless") 
driver = webdriver.Chrome(options=options)

def get_text_by_css(selector):
    """Helper to find text safely"""
    try:
        element = driver.find_element(By.CSS_SELECTOR, selector)
        return element.text
    except:
        return "Not Found"

def scrape_google_maps():
    driver.get(f"https://www.google.com/maps/search/{QUERY.replace(' ', '+')}")
    wait = WebDriverWait(driver, 15)
    
    # 1. Wait for the list to load
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "hfpxzc")))
    
    results = []
    
    # 2. Find all listing result links
    listings = driver.find_elements(By.CLASS_NAME, "hfpxzc")
    
    for index, listing in enumerate(listings[:10]): # Start with 10 for testing
        try:
            # Scroll item into view and click
            driver.execute_script("arguments[0].scrollIntoView();", listing)
            time.sleep(1)
            listing.click()
            
            # 3. Wait specifically for the Title of the PG to appear in the side panel
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1.DUwDvf")))
            time.sleep(2) # Extra buffer for address/phone to load
            
            # --- EXTRACTION ---
            name = get_text_by_css("h1.DUwDvf")
            
            # Google Maps stores Address/Phone in a common class 'Io6YTe'
            # We search all elements with that class and pick by context
            info_elements = driver.find_elements(By.CLASS_NAME, "Io6YTe")
            
            address = "Not Found"
            phone = "Not Found"
            
            for el in info_elements:
                text = el.text
                if len(text) > 5 and "," in text: # Likely an address
                    address = text
                if text.replace(" ", "").replace("+", "").isdigit() or text.startswith("+"):
                    phone = text

            results.append({
                "PG Name": name,
                "Address": address,
                "Contact No": phone,
                "Location Link": driver.current_url
            })
            print(f"[{index+1}] Saved: {name}")

        except Exception as e:
            print(f"[{index+1}] Failed to extract details. Skipping...")
            continue

    return results

# --- Run ---
data = scrape_google_maps()
if data:
    pd.DataFrame(data).to_csv(OUTPUT, index=False)
    print(f"\n✅ Success! Check {OUTPUT}")
else:
    print("No data found.")

driver.quit()