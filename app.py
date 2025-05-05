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
    # Use the correct parameter names for the FindHCPs tool
    results = nova.maps_finder.search_and_get_details(query=specialty, location=city)
    
    if not results:
        return "No healthcare professionals found for the given criteria."
    
    # Format results
    formatted_results = []
    for hcp in results:
        formatted_results.append(
            f"Name: {hcp.get('name')} | Phone: {hcp.get('phone', 'N/A')} | Website: {hcp.get('website', 'N/A')}"
        )
    
    return "\n".join(formatted_results)

def get_specialties():
    """Get unique specialties from the HCP data."""
    return sorted(nova.hcp_data['specialty'].unique().tolist())

def get_cities():
    """Get unique cities from the HCP data."""
    return sorted(nova.hcp_data['city'].unique().tolist())

def generate_message(name, specialty, city):
    """Generate a personalized message for an HCP."""
    return nova._generate_personalized_message(name, specialty, city)

def record_contact(hcp_id):
    """Record that an HCP has been contacted."""
    try:
        hcp_id = int(hcp_id)
        return nova._update_contact_record(hcp_id)
    except ValueError:
        return "Error: HCP ID must be a number."

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
                hcp_name_input = gr.Textbox(label="HCP Name")
                hcp_specialty_input = gr.Textbox(label="HCP Specialty")
                hcp_city_input = gr.Textbox(label="HCP City")
                generate_button = gr.Button("Generate Message")
            
            outreach_text = gr.Textbox(label="Personalized Message", lines=10)
            
            generate_button.click(
                generate_message,
                [hcp_name_input, hcp_specialty_input, hcp_city_input],
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
        
        For more information, see the [GitHub repository](https://github.com/AI-Agent-Incubator-Month/cdt-nbse).
        """)
    
    return interface

# Start the app
if __name__ == "__main__":
    interface = create_interface()
    interface.launch(share=True)