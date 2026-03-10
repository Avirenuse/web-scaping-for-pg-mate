import requests
import pandas as pd
import os

API_KEY = "AIzaSyAvSR7PVcIiC-Te4QM3m4CA03s6QCQQYlY"

location = "Sangli"
query = "PG hostel in " + location

url = "https://maps.googleapis.com/maps/api/place/textsearch/json"

params = {
    "query": query,
    "key": API_KEY
}

file_path = "PG_List.xlsx"

if os.path.exists(file_path):
    os.remove(file_path)

response = requests.get(url, params=params)
data = response.json()

print(data)   # debug output

pg_data = []

for i, place in enumerate(data.get('results', []), start=1):

    name = place.get('name')
    address = place.get('formatted_address')
    place_id = place.get('place_id')

    maps_link = f"https://www.google.com/maps/place/?q=place_id:{place_id}"

    pg_data.append({
        "Sr. no": i,
        "PG name": name,
        "Contact No Pg": "Not Available",
        "Located Area": address,
        "Link": maps_link
    })

df = pd.DataFrame(pg_data)

# df.to_excel("output_PG_List.xlsx", index=False)
df.to_excel(file_path, index=False)

print("Data saved successfully")