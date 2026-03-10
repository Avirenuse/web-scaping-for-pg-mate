import requests
import pandas as pd
import os
import time

# --- CONFIGURATION ---
# IMPORTANT: Delete your old API key from Google Cloud Console and paste a NEW one here.
API_KEY = "YOUR_NEW_GOOGLE_MAPS_API_KEY"
LOCATION = "Sangli"
QUERY = f"PG hostel in {LOCATION}"
FILE_PATH = "PG_List.xlsx"

def get_pg_data():
    search_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    details_url = "https://maps.googleapis.com/maps/api/place/details/json"
    
    params = {
        "query": QUERY,
        "key": API_KEY
    }

    try:
        # Initial Search Request
        response = requests.get(search_url, params=params)
        response.raise_for_status()
        search_data = response.json()

        if search_data.get("status") != "OK":
            print(f"API Error: {search_data.get('status')} - {search_data.get('error_message', 'No message')}")
            return

        pg_results = []
        
        for i, place in enumerate(search_data.get('results', []), start=1):
            place_id = place.get('place_id')
            name = place.get('name')
            address = place.get('formatted_address')

            # Secondary request to get the Phone Number (not included in basic text search)
            detail_params = {
                "place_id": place_id,
                "fields": "formatted_phone_number",
                "key": API_KEY
            }
            detail_resp = requests.get(details_url, params=detail_params).json()
            phone = detail_resp.get('result', {}).get('formatted_phone_number', "Not Available")

            # Official Google Maps Link format
            maps_link = f"https://www.google.com/maps/search/?api=1&query={name.replace(' ', '+')}&query_place_id={place_id}"

            pg_results.append({
                "Sr. no": i,
                "PG name": name,
                "Contact No Pg": phone,
                "Located Area": address,
                "Link": maps_link
            })
            
            # Tiny sleep to avoid hitting rate limits if the list is long
            time.sleep(0.1)

        # Save to Excel
        if pg_results:
            df = pd.DataFrame(pg_results)
            df.to_excel(FILE_PATH, index=False)
            print(f"Successfully saved {len(pg_results)} PG listings to {FILE_PATH}")
        else:
            print("No results found.")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    # Clean up old file if it exists
    if os.path.exists(FILE_PATH):
        os.remove(FILE_PATH)
        
    get_pg_data()