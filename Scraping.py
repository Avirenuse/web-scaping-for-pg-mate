import pandas as pd
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

QUERY = "PG in Sangli Maharashtra"
OUTPUT = "sangli_pg.csv"

options = Options()
options.add_argument("--start-maximized")

driver = webdriver.Chrome(options=options)


# ---- CLEAN TEXT FUNCTION ----
def clean_text(text):
    if not text:
        return "NA"
    
    text = text.strip()
    
    # remove emojis / special icons
    text = re.sub(r'[^\x00-\x7F]+', '', text)

    return text


def scrape_clean_data():

    driver.get(f"https://www.google.com/maps/search/{QUERY.replace(' ','+')}")
    time.sleep(5)

    scrollable_div = driver.find_element(By.CSS_SELECTOR, 'div[role="feed"]')

    for _ in range(10):
        driver.execute_script(
            "arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div
        )
        time.sleep(2)

    items = driver.find_elements(By.CSS_SELECTOR, "a.hfpxzc")

    results = []

    for index, item in enumerate(items):

        try:
            driver.execute_script("arguments[0].click();", item)
            time.sleep(3)

            # PG Name
            try:
                name = clean_text(driver.find_element(By.CSS_SELECTOR, "h1.DUwDvf").text)
            except:
                name = "NA"

            # Address
            try:
                address = clean_text(
                    driver.find_element(By.CSS_SELECTOR, 'button[data-item-id="address"]').text
                )
            except:
                address = "NA"

            # Phone
            try:
                phone = clean_text(
                    driver.find_element(By.CSS_SELECTOR, 'button[data-item-id^="phone"]').text
                )
            except:
                phone = "NA"

            results.append(
                {
                    "Sr No": index + 1,
                    "PG Name": name,
                    "Address": address,
                    "Contact No": phone,
                    "Map Link": driver.current_url,
                }
            )

            print(f"Captured {index+1}: {name}")

        except Exception:
            continue

    return results


data = scrape_clean_data()

if data:
    df = pd.DataFrame(data)
    df.to_csv(OUTPUT, index=False, encoding="utf-8-sig")
    print("\n✅ Clean data saved to", OUTPUT)

driver.quit()