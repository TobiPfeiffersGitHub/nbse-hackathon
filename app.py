from dotenv import load_dotenv
import os
import streamlit as st
from streamlit_folium import st_folium
import folium
import requests
import pandas as pd
import time

load_dotenv()

API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def find_cardiologists_tool(southwest, northeast):
    query = "cardiologist"
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    location = (
        (southwest[0] + northeast[0]) / 2,
        (southwest[1] + northeast[1]) / 2
    )
    radius = 50000

    params = {
        "query": query,
        "location": f"{location[0]},{location[1]}",
        "radius": radius,
        "key": API_KEY
    }

    results = []
    while True:
        response = requests.get(url, params=params)
        data = response.json()
        for place in data.get("results", []):
            place_id = place["place_id"]
            details = get_place_details(place_id)
            if details:
                results.append(details)

        if "next_page_token" in data:
            time.sleep(2)
            params["pagetoken"] = data["next_page_token"]
        else:
            break

    return pd.DataFrame(results)

def get_place_details(place_id):
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "fields": "name,formatted_phone_number,website",
        "key": API_KEY
    }
    response = requests.get(url, params=params)
    result = response.json().get("result", {})
    return {
        "name": result.get("name"),
        "phone": result.get("formatted_phone_number"),
        "website": result.get("website")
    }

# Streamlit Interface
st.title("Cardiologist Finder via Bounding Box")

m = folium.Map(location=[37.77, -122.42], zoom_start=12)
draw = folium.plugins.Draw(export=True)
draw.add_to(m)
output = st_folium(m, width=700, height=500, returned_objects=["last_drawn"])

if st.button("Search Cardiologists") and output and "geometry" in output["last_drawn"]:
    bounds = output["last_drawn"]["geometry"]["coordinates"][0]
    lats = [coord[1] for coord in bounds]
    lngs = [coord[0] for coord in bounds]
    southwest = (min(lats), min(lngs))
    northeast = (max(lats), max(lngs))

    st.write("Searching in bounding box:", southwest, "to", northeast)
    results_df = find_cardiologists_tool(southwest, northeast)
    st.dataframe(results_df)
    st.download_button("Download CSV", results_df.to_csv(index=False), "results.csv")