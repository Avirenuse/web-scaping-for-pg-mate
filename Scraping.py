import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

QUERY = "PG in Sangli Maharashtra"
OUTPUT = "sangli_pg_clean.csv"

options = Options()
options.add_argument("--start-maximized")

driver = webdriver.Chrome(options=options)


def scrape_clean_data():

    driver.get(f"https://www.google.com/maps/search/{QUERY.replace(' ','+')}")
    time.sleep(5)

    # Scroll listing panel
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
                name = driver.find_element(By.CSS_SELECTOR, "h1.DUwDvf").text
            except:
                name = "NA"

            address = "NA"
            phone = "NA"

            # Address
            try:
                address = driver.find_element(
                    By.CSS_SELECTOR, 'button[data-item-id="address"]'
                ).text
            except:
                pass

            # Phone
            try:
                phone = driver.find_element(
                    By.CSS_SELECTOR, 'button[data-item-id^="phone"]'
                ).text
            except:
                pass

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

        except Exception as e:
            print("Error:", e)
            continue

    return results


data = scrape_clean_data()

if data:
    df = pd.DataFrame(data)
    df.to_csv(OUTPUT, index=False, encoding="utf-8-sig")
    print("\n✅ Data saved to", OUTPUT)
else:
    print("No data found")

driver.quit()