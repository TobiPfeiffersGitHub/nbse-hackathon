import gradio as gr
from agent import NovaAgent
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize the Nova agent
nova = NovaAgent()

def process_message(message, history):
    """Process a message from the user and return Nova's response."""
    try:
        response = nova.run(message)
        return response
    except Exception as e:
        return f"I apologize, but I encountered an error: {str(e)}. Let's try a different approach."

def search_hcps(specialty, city):
    """Search for HCPs with specific specialty and city."""
    query = {}
    if specialty:
        query['specialty'] = specialty
    if city:
        query['city'] = city
        
    results = nova._query_hcp_database(query)
    
    if isinstance(results, str):
        return results
    
    # Format results
    formatted_results = []
    for hcp in results:
        status = "Contacted" if hcp.get('contacted') else "Not Contacted"
        formatted_results.append(
            f"ID: {hcp.get('hcp_id')} | {hcp.get('name')} | {hcp.get('specialty')} | "
            f"{hcp.get('city')} | {hcp.get('preferred_channel')} | {status}"
        )
    
    return "\n".join(formatted_results) if formatted_results else "No results found."

def get_specialties():
    """Get unique specialties from the HCP data."""
    return sorted(nova.hcp_data['specialty'].unique().tolist())

def get_cities():
    """Get unique cities from the HCP data."""
    return sorted(nova.hcp_data['city'].unique().tolist())

def generate_message(hcp_id):
    """Generate a personalized message for an HCP."""
    return nova._generate_personalized_message(hcp_id)

def record_contact(hcp_id):
    """Record that an HCP has been contacted."""
    return nova._update_contact_record(hcp_id)

def create_interface():
    """Create the Gradio interface."""
    with gr.Blocks(title="Nova - Pharmaceutical HCP Engagement Assistant") as interface:
        gr.Markdown("# Nova: Next-generation Outreach Virtual Assistant")
        gr.Markdown("### Your AI partner for engaging healthcare professionals with research-backed personalized outreach")
        
        with gr.Tab("Chat with Nova"):
            chatbot = gr.Chatbot(height=400)
            msg = gr.Textbox(label="Message Nova", placeholder="How can I help you engage with healthcare professionals today?")
            clear = gr.Button("Clear Chat")
            
            # Update the chatbot interface
            def respond(message, chat_history):
                bot_message = process_message(message, chat_history)
                chat_history.append((message, bot_message))
                return "", chat_history
            
            msg.submit(
                respond, 
                [msg, chatbot], 
                [msg, chatbot]
            )
            
            clear.click(lambda: None, None, chatbot, queue=False)
        
        with gr.Tab("HCP Search"):
            with gr.Row():
                specialty_dropdown = gr.Dropdown(choices=get_specialties(), label="Specialty")
                city_dropdown = gr.Dropdown(choices=get_cities(), label="City")
            
            search_button = gr.Button("Search HCPs")
            results_text = gr.Textbox(label="Results", lines=10)
            
            search_button.click(
                search_hcps,
                [specialty_dropdown, city_dropdown],
                [results_text]
            )
        
        with gr.Tab("Quick Actions"):
            gr.Markdown("### Generate Personalized Outreach")
            
            with gr.Row():
                hcp_id_input = gr.Textbox(label="HCP ID")
                generate_button = gr.Button("Generate Message")
            
            outreach_text = gr.Textbox(label="Personalized Message", lines=10)
            
            generate_button.click(
                generate_message,
                [hcp_id_input],
                [outreach_text]
            )
            
            gr.Markdown("### Record Contact")
            
            with gr.Row():
                record_id_input = gr.Textbox(label="HCP ID to Mark as Contacted")
                record_button = gr.Button("Record Contact")
            
            record_status = gr.Textbox(label="Status")
            
            record_button.click(
                record_contact,
                [record_id_input],
                [record_status]
            )
            
        gr.Markdown("### Project Information")
        gr.Markdown("""
        **Nova** was developed during the Pharma-HCP Engagement Hackathon to revolutionize how 
        pharmaceutical companies connect with healthcare professionals. The system combines:
        
        1. **HCP Database Management**: Track healthcare professionals, their specialties, and communication preferences
        2. **PubMed Research Integration**: Automatically incorporate relevant medical research
        3. **AI-Powered Personalization**: Generate tailored outreach messages
        4. **Google Maps Discovery**: Find new healthcare professionals in target locations
        
        For more information, see the [GitHub repository](https://github.com/yourusername/nova-hcp-assistant).
        """)
    
    return interface

# Start the app
if __name__ == "__main__":
    interface = create_interface()
    interface.launch(share=True)