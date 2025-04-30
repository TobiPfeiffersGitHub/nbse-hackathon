from crewai import Agent
from tools.google_maps_finder import GoogleMapsFinder

scraper_agent = Agent(
    role="Scraper",
    goal="Scrape new HCP profiles from external sources.",
    backstory="An expert in mining professional data for healthcare providers.",
    tools=[GoogleMapsFinder],
    verbose=True
)