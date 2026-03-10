import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# --- Setup ---
QUERY = "PG in Sangli Maharashtra"
OUTPUT = "sangli_pg_clean.csv"

options = Options()
driver = webdriver.Chrome(options=options)

def scrape_clean_data():
    driver.get(f"https://www.google.com/maps/search/{QUERY.replace(' ', '+')}")
    time.sleep(5)
    
    # Scroll to load listings
    scrollable_div = driver.find_element(By.CSS_SELECTOR, 'div[role="feed"]')
    for _ in range(8): # Scroll 8 times to get a good list
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div)
        time.sleep(2)

    items = driver.find_elements(By.CLASS_NAME, "hfpxzc")
    results = []

    for index, item in enumerate(items):
        try:
            driver.execute_script("arguments[0].click();", item)
            time.sleep(2.5) 

            # 1. Get Name
            try:
                name = driver.find_element(By.CSS_SELECTOR, "h1.DUwDvf").text
            except:
                name = "NA"

            # 2. Get Address & Phone (Better Logic to avoid emojis)
            address = "NA"
            phone = "NA"
            
            # We look for the specific 'aria-label' which contains clean text
            info_elements = driver.find_elements(By.CLASS_NAME, "CsS9M") 
            
            for el in info_elements:
                text_content = el.text
                # Address usually contains commas
                if "," in text_content and len(text_content) > 10:
                    address = text_content
                # Phone contains numbers
                clean_phone = text_content.replace(" ", "").replace("+", "").replace("-", "")
                if clean_phone.isdigit() and len(clean_phone) >= 10:
                    phone = text_content

            results.append({
                "Sr. no": index + 1,
                "PG name": name,
                "Contact No Pg": phone,
                "Located Area": address,
                "Link": driver.current_url
            })
            print(f"Captured {index+1}: {name}")

        except Exception as e:
            continue

    return results

# --- Run and Save with Excel-friendly encoding ---
data = scrape_clean_data()
if data:
    df = pd.DataFrame(data)
    # 'utf-8-sig' prevents those weird symbols from appearing in Excel
    df.to_csv(OUTPUT, index=False, encoding='utf-8-sig')
    print(f"\n✅ Clean data saved to {OUTPUT}")
else:
    print("No data found.")

driver.quit()