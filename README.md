## Nova: Next-Generation Pharmaceutical HCP Engagement Assistant
Nova is an AI-powered assistant designed to revolutionize how pharmaceutical companies connect with healthcare professionals (HCPs). Built during the Pharma-HCP Engagement Hackathon, Nova combines multiple technologies to provide intelligent, personalized outreach capabilities.
 
### Features:
- **AI-Powered Conversations:** Engage with Nova using natural language to find HCPs, research medical content, and generate outreach materials
- **HCP Database Management:** Track healthcare professionals, their specialties, and communication preferences
- **PubMed Research Integration:** Automatically incorporate relevant medical research into outreach messaging
- **Google Maps Discovery:** Find new healthcare professionals in target locations
- **Personalized Outreach Generation:** Create tailored messages for different HCP specialties and locations
 
### System Requirements:
- Python 3.8+
- OpenAI API key
- Google Maps API key
- NCBI Entrez email and API key (optional, for higher rate limits)
 
### Project Structure:
- `agent.py`: Core Nova agent with LangChain integration  
- `app.py`: Gradio web interface  
- `data/`: Contains HCP database (CSV format)  
- `tools/`: Tool implementations  
  - `google_maps_finder.py`: Google Maps API integration  
  - `nova.py`: PubMed search functionality  
  - `personalized_outreach.py`: Outreach message generation  
  - `record_tool.py`: Database management utilities
 
### Example Interactions
You: Find cardiologists in Hamburg
 
Nova: I've found 3 cardiologists in Hamburg:
- Dr. Max Wolf | Phone: +49 40 1234567 | Website: https://example.com
- Dr. Leon Weber | Phone: +49 40 7654321 | Website: N/A 
- Dr. Nico Becker | Phone: +49 40 9876543 | Website: https://cardio-example.com
You: Generate a personalized outreach for Dr. Wolf in cardiology from Hamburg
 
Nova: 
Dear Dr. Max Wolf,
 
As a specialist in cardiology based in Hamburg, we believe our latest insights could be highly relevant to your practice.
 
Recent research you might find valuable:
"Recent Advances in Early Detection of Cardiovascular Disease"
https://pubmed.ncbi.nlm.nih.gov/12345678/
 
Let us know if you'd like to explore further.
 
Best regards,
Your Outreach Team
