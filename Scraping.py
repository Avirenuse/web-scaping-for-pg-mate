import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains

# --- Setup ---
QUERY = "PG in Vadodara Gujarat"
OUTPUT = "Vadodara_all_pgs.csv"

options = Options()
# options.add_argument("--headless") 
driver = webdriver.Chrome(options=options)

def scrape_sangli():
    driver.get(f"https://www.google.com/maps/search/{QUERY.replace(' ', '+')}")
    time.sleep(5) # Wait for initial load
    
    # 1. SCROLLING LOOP - This forces Google to load ALL results
    print("🔄 Scrolling to find all PGs... please wait.")
    scrollable_div = driver.find_element(By.CSS_SELECTOR, 'div[role="feed"]')
    
    for _ in range(10): # Adjust range higher if you want even more results
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div)
        time.sleep(2) # Give it time to load new items

    # 2. COLLECT ALL ITEMS
    items = driver.find_elements(By.CLASS_NAME, "hfpxzc")
    print(f"📊 Found {len(items)} listings. Starting extraction...")
    
    results = []

    for index, item in enumerate(items):
        try:
            # Click the item to open details
            driver.execute_script("arguments[0].click();", item)
            time.sleep(2.5) # Wait for the side panel to refresh

            # Extract Name
            try:
                name = driver.find_element(By.CSS_SELECTOR, "h1.DUwDvf").text
            except:
                name = "Unknown Name"

            # Extract Address & Phone using specific data-item-ids
            address = "NA"
            phone = "NA"
            
            # Google Maps uses specific IDs for these buttons
            try:
                addr_element = driver.find_element(By.CSS_SELECTOR, "[data-item-id='address']")
                address = addr_element.text
            except:
                pass

            try:
                phone_element = driver.find_element(By.CSS_SELECTOR, "[data-tooltip='Copy phone number']")
                phone = phone_element.text
            except:
                # Secondary check for phone if the button isn't there
                info_elements = driver.find_elements(By.CLASS_NAME, "Io6YTe")
                for el in info_elements:
                    if el.text.replace(" ", "").replace("+", "").isdigit():
                        phone = el.text

            results.append({
                "PG Name": name,
                "Address": address,
                "Contact No": phone,
                "Map Link": driver.current_url
            })
            print(f"[{index + 1}] Scraped: {name} | Phone: {phone}")

        except Exception as e:
            print(f"[{index + 1}] Error on this item, skipping...")
            continue

    return results

# --- Run and Save ---
final_list = scrape_sangli()

if final_list:
    df = pd.DataFrame(final_list)
    # Remove duplicates to be safe
    df = df.drop_duplicates(subset=['PG Name', 'Address'])
    df.to_csv(OUTPUT, index=False)
    print(f"\n✅ Finished! {len(df)} PGs saved to {OUTPUT}")
else:
    print("No data found.")

driver.quit()

