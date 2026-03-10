import requests
import pandas as pd

API_KEY = "AIzaSyAvSR7PVcIiC-Te4QM3m4CA03s6QCQQYlY"

location = "Sangli"
query = "PG hostel in " + location

url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={query}&key={API_KEY}"

response = requests.get(url)
data = response.json()

pg_data = []

for i, place in enumerate(data['results'], start=1):
    
    name = place.get('name')
    address = place.get('formatted_address')
    place_id = place.get('place_id')
    
    # Get phone number using details API
    details_url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=formatted_phone_number&key={API_KEY}"
    
    details_response = requests.get(details_url)
    details_data = details_response.json()
    
    phone = details_data.get("result", {}).get("formatted_phone_number", "Not Available")
    
    maps_link = f"https://www.google.com/maps/place/?q=place_id:{place_id}"
    
    pg_data.append({
        "Sr. no": i,
        "PG name": name,
        "Contact No Pg": phone,
        "Located Area": address,
        "Link": maps_link
    })

df = pd.DataFrame(pg_data)

df.to_excel("PG_List.xlsx", index=False)

print("Data saved to PG_List.xlsx")