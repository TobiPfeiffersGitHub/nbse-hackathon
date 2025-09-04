# tools.py - Defines tools for the Nova agent

import logging
import os
from Bio import Entrez
from Bio import Medline  # Correct import for Medline parser
from urllib.error import HTTPError, URLError
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# --- NCBI Entrez Configuration ---
# IMPORTANT: Set your email address here. NCBI requires this.
# It's good practice to let them know who is using their services.
# Set your email via the ENTREZ_EMAIL environment variable
# ENTREZ_EMAIL = "your_email@example.com"
ENTREZ_EMAIL = os.getenv("ENTREZ_EMAIL")
Entrez.email = ENTREZ_EMAIL

# Retrieve NCBI API Key from environment variable
# IMPORTANT: Set the NCBI_API_KEY environment variable for higher request
# limits. You can obtain a key from:
# https://www.ncbi.nlm.nih.gov/account/settings/
NCBI_API_KEY = os.getenv("NCBI_API_KEY")
if NCBI_API_KEY:
    Entrez.api_key = NCBI_API_KEY
    logger.info("Using NCBI API Key from environment variable.")
else:
    logger.warning(
        "NCBI_API_KEY environment variable not set. "
        "Requests will be made without an API key, "
        "which may result in lower rate limits."
    )
# --- End NCBI Entrez Configuration ---


class PubMedSearchTool:
    """
    A tool to search PubMed for medical research articles using the NCBI
    Entrez API. Requires the 'biopython' library.
    Retrieves the NCBI API key from the 'NCBI_API_KEY' environment variable.
    """
    def __init__(self):
        """
        Initialize the PubMed search tool.
        Sets up NCBI Entrez email and API key (if available).
        """
        # Initialization logic moved to the module level for Entrez setup
        logger.info(
            "PubMedSearchTool initialized. Using Entrez email: %s",
            Entrez.email
        )
        if Entrez.api_key:
            logger.info("NCBI API Key is configured.")

    def _parse_article(self, medline_record: dict) -> dict | None:
        """
        Parses a single PubMed article record dict (from Bio.Medline.parse)
        into the desired format.
        """
        try:
            # Extract fields using common Medline keys, providing defaults
            pmid = medline_record.get('PMID', '')
            title = medline_record.get('TI', 'N/A')
            authors = medline_record.get('AU', [])  # Usually 'AU' key
            # Date Published ('DP') is common, fallback to Entrez Date ('EDAT')
            date = medline_record.get('DP', medline_record.get('EDAT', 'N/A'))
            # Abstract ('AB') is the standard key
            abstract = medline_record.get('AB', 'N/A')

            # Construct URL
            url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else "N/A"

            # Basic validation: Check for essential fields (PMID, Title)
            if not pmid and title == 'N/A':
                source = medline_record.get('SO', 'Unknown Source')
                logger.warning(
                    f"Skipping record with missing PMID and Title: {source}"
                )
                return None  # Skip records missing essential info

            return {
                'pmid': pmid,
                'title': title,
                'authors': authors,  # Already a list from Medline.parse
                'date': str(date),  # Ensure date is string
                'abstract': str(abstract),  # Ensure abstract is string
                'url': url
            }
        except Exception as e:
            pmid_unknown = medline_record.get('PMID', 'UNKNOWN')
            logger.error(
                f"Error parsing article PMID {pmid_unknown}: {e}",
                exc_info=True
            )
            return None  # Return None if parsing fails for an article

    def search(self, query: str, max_results: int = 10) -> list[dict]:
        """
        Performs a search on PubMed using NCBI Entrez E-utilities.

        Args:
            query (str): The search query string (e.g.,
                         "PCSK9 inhibitors clinical trials 2024").
            max_results (int): The maximum number of results to retrieve.

        Returns:
            list[dict]: A list of dictionaries, each representing a found
                        article with keys like 'pmid', 'title', 'authors',
                        'date', 'abstract', 'url'. Returns an empty list if
                        an error occurs or no results are found.
        """
        logger.info(
            f"Executing PubMed search for query: '{query}' "
            f"with max_results={max_results}"
        )
        results = []
        try:
            # 1. Use esearch to find PMIDs matching the query
            handle = Entrez.esearch(
                db="pubmed",
                term=query,
                retmax=str(max_results),
                sort="relevance"
            )
            search_results = Entrez.read(handle)
            handle.close()
            id_list = search_results.get("IdList", [])

            if not id_list:
                logger.info(f"No PubMed IDs found for query: '{query}'")
                return []

            logger.info(f"Found {len(id_list)} PMIDs, fetching details...")

            # 2. Use efetch to retrieve details for those PMIDs
            # (MEDLINE format) Using rettype='medline' and retmode='text'
            # works well with Bio.Entrez.Medline.parse
            handle = Entrez.efetch(
                db="pubmed", id=id_list, rettype="medline", retmode="text"
            )
            # Using Medline parser which handles the text format well
            records = Medline.parse(handle)
            records = list(records)  # Consume the generator
            handle.close()

            logger.info(f"Retrieved {len(records)} records from efetch.")

            # 3. Parse the results into the desired dictionary format
            for record in records:
                parsed_article = self._parse_article(record)
                if parsed_article:  # Only add if parsing was successful
                    results.append(parsed_article)

        except HTTPError as e:
            logger.error(
                f"HTTP Error during PubMed search: {e.code} {e.reason}",
                exc_info=True
            )
            # Consider raising a specific exception or returning error info
            return []
        except URLError as e:
            logger.error(
                f"URL Error during PubMed search (Network issue?): {e.reason}",
                exc_info=True
            )
            return []
        except RuntimeError as e:
            # Entrez.read can raise RuntimeError on parsing errors
            logger.error(
                f"Runtime Error parsing Entrez results: {e}", exc_info=True
            )
            return []
        except Exception as e:
            # Catch any other unexpected errors during the process
            logger.error(
                f"An unexpected error occurred during PubMed search: {e}",
                exc_info=True
            )
            return []  # Return empty list on generic error

        logger.info(
            f"Successfully parsed {len(results)} articles for query: '{query}'"
        )
        return results


# Example usage (for testing the tool directly)
if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # Ensure NCBI_API_KEY is set as an environment variable before running this
    if not NCBI_API_KEY:
        print("\nWARNING: NCBI_API_KEY environment variable is not set.")
        print("You can still run the search, but may encounter rate limits.")
        print("Get a key: https://www.ncbi.nlm.nih.gov/account/settings/\n")
    else:
        # Show last 4 chars for confirmation
        print(f"\nUsing NCBI API Key: ...{NCBI_API_KEY[-4:]}")

    # The tool now reads the email and API key internally
    tool = PubMedSearchTool()

    # Example Queries:
    # search_query = "COVID-19 vaccine efficacy"
    search_query = "Familial hypercholesterolemia diagnosis guidelines"
    # search_query = "NonExistentTerm12345ZZZ" # Test no results
    # search_query = "PCSK9 inhibitors clinical trials 2024"

    print(f"Searching PubMed for: '{search_query}' (max 5 results)")
    articles = tool.search(search_query, max_results=5)

    if articles:
        print(f"\nFound {len(articles)} articles:")
        for i, article in enumerate(articles, 1):
            print(f"\n--- Article {i} ---")
            print(f"  PMID: {article.get('pmid')}")
            print(f"  Title: {article.get('title')}")
            # Join authors list for display
            print(f"  Authors: {', '.join(article.get('authors', []))}")
            print(f"  Date: {article.get('date')}")
            print(f"  URL: {article.get('url')}")
            abstract = article.get('abstract', 'N/A')
            print(
                f"  Abstract: {abstract[:150]}..."
                if len(abstract) > 150 else abstract
            )
    else:
        print(
            f"\nNo articles found or an error occurred for '{search_query}'. "
            f"Check logs for details."
        )

    # Example with a different query
    search_query_2 = "CRISPR gene editing safety"
    print(f"\nSearching PubMed for: '{search_query_2}' (max 3 results)")
    articles_2 = tool.search(search_query_2, max_results=3)
    if articles_2:
        print(f"\nFound {len(articles_2)} articles:")
        for i, article in enumerate(articles_2, 1):
            print(f"\n--- Article {i} ---")
            print(f"  PMID: {article.get('pmid')}")
            print(f"  Title: {article.get('title')}")
            # Only show first 2 authors for brevity in example
            authors_str = ', '.join(article.get('authors', [])[:2])
            if len(article.get('authors', [])) > 2:
                authors_str += ", et al."
            print(f"  Authors: {authors_str}")
            print(f"  Date: {article.get('date')}")
    else:
        # Wrap the long print statement
        print(
            f"\nNo articles found or an error occurred for "
            f"'{search_query_2}'. Check logs for details."
        )