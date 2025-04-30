from tools.nova import PubMedSearchTool

class PersonalizedOutreachGenerator:
    """
    Combines PubMed enrichment and profile-based content generation
    into a single callable class.
    """

    def __init__(self):
        self.pubmed = PubMedSearchTool()

    def generate_message(self, hcp_profile: dict) -> str:
        """
        Given an HCP profile dict, returns a personalized outreach message
        with relevant PubMed research included.
        """
        name = hcp_profile.get("name", "Doctor")
        specialty = hcp_profile.get("specialty", "your field")
        city = hcp_profile.get("city", "your area")

        # Fetch relevant article
        query = f"{specialty} treatment guidelines 2024"
        articles = self.pubmed.search(query, max_results=1)
        article_text = ""

        if articles:
            top_article = articles[0]
            article_text = (
                f"\n\nRecent research you might find valuable:\n"
                f"\"{top_article['title']}\"\n"
                f"{top_article['url']}"
            )

        message = (
            f"Dear {name},\n\n"
            f"As a specialist in {specialty} based in {city}, "
            f"we believe our latest insights could be highly relevant to your practice."
            f"{article_text}\n\n"
            f"Let us know if you’d like to explore further.\n\n"
            f"Best regards,\nYour Outreach Team"
        )

        return message
