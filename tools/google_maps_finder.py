import googlemaps
from langchain.tools import Tool

class GoogleMapsFinder:
    def __init__(self, api_key):
        self.gmaps = googlemaps.Client(key=api_key)

    def search_and_get_details(self, query: str, location: str = ""):
        search_query = f"{query} in {location}" if location else query
        results = self.gmaps.places(query=search_query)
        output = []
        for place in results.get('results', []):
            place_id = place['place_id']
            details = self.gmaps.place(
                place_id=place_id,
                fields=['name', 'formatted_phone_number', 'website']
            )
            result = details.get('result', {})
            if result:
                output.append({
                    "name": result.get("name"),
                    "phone": result.get("formatted_phone_number"),
                    "website": result.get("website")
                })
        return output[:5]  # Limit for brevity

    def get_tool(self):
        return Tool(
            name="Google Maps Finder",
            func=lambda query, location="": self.search_and_get_details(query, location),
            description="Use this tool to find professionals and their contact details. Input: search term and optional location, e.g., 'cardiologists' or 'cardiologists, Frankfurt'."
        )
