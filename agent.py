import os
import pandas as pd
import json
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import Tool, tool
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.agents import AgentExecutor, create_json_chat_agent
from langchain.tools import StructuredTool
from pydantic import BaseModel

# Import our custom tools
from tools.google_maps_finder import GoogleMapsFinder
from tools.nova import PubMedSearchTool
from tools.personalized_outreach import PersonalizedOutreachGenerator
from tools.record_tool import get_outreach_candidates

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

class FindHCPsInput(BaseModel):
    specialty: str
    location: str = ""

class SearchPubMedInput(BaseModel):
    query: str
    max_results: int = 10

class OutreachInput(BaseModel):
    name: str
    specialty: str
    city: str

class RecordContactInput(BaseModel):
    hcp_id: int

class HCPQueryInput(BaseModel):
    specialty: str = ""
    city: str = ""
    contacted: bool | None = None

class NovaAgent:
    def __init__(self):
        self.llm = ChatOpenAI(
            temperature=0.2,
            api_key=OPENAI_API_KEY,
            model="gpt-4o"
        )

        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )

        self.hcp_data = pd.read_csv('data/hcp_combined.csv')

        self.pubmed_tool = PubMedSearchTool()
        self.maps_finder = GoogleMapsFinder(api_key=GOOGLE_API_KEY)
        self.outreach_generator = PersonalizedOutreachGenerator()

        self.tools = self._create_tools()
        self.agent = self._create_agent()

        self.agent_executor = AgentExecutor.from_agent_and_tools(
            agent=self.agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=5
        )

    def _create_tools(self):
        return [
            StructuredTool.from_function(
                name="FindHCPs",
                description="Find healthcare professionals by specialty and location.",
                func=self.maps_finder.search_and_get_details,
                args_schema=FindHCPsInput
            ),
            StructuredTool.from_function(
                name="SearchMedicalLiterature",
                description="Search for medical research papers on PubMed.",
                func=lambda query, max_results=10: self.pubmed_tool.search(query, max_results),
                args_schema=SearchPubMedInput
            ),
            StructuredTool.from_function(
                name="GeneratePersonalizedOutreach",
                description="Generate a personalized outreach message for a healthcare professional.",
                func=self._generate_personalized_message,
                args_schema=OutreachInput
            ),
            StructuredTool.from_function(
                name="GetOutreachCandidates",
                description="Get a list of healthcare professionals who have not been contacted yet.",
                func=lambda: get_outreach_candidates(),
                args_schema=None
            ),
            StructuredTool.from_function(
                name="RecordContact",
                description="Record that a healthcare professional has been contacted.",
                func=self._update_contact_record,
                args_schema=RecordContactInput
            ),
            StructuredTool.from_function(
                name="QueryHCPDatabase",
                description="Query the HCP database for specific criteria.",
                func=self._query_hcp_database,
                args_schema=HCPQueryInput
            )
        ]

    def _generate_personalized_message(self, name: str, specialty: str, city: str):
        return self.outreach_generator.generate_message({
            "name": name,
            "specialty": specialty,
            "city": city
        })

    def _update_contact_record(self, hcp_id: int):
        if hcp_id in self.hcp_data['hcp_id'].values:
            self.hcp_data.loc[self.hcp_data['hcp_id'] == hcp_id, 'contacted'] = True
            self.hcp_data.to_csv('data/hcp_combined.csv', index=False)
            return f"HCP {hcp_id} marked as contacted successfully."
        return f"HCP ID {hcp_id} not found."

    def _query_hcp_database(self, specialty: str = "", city: str = "", contacted: bool | None = None):
        df = self.hcp_data.copy()
        if specialty:
            df = df[df['specialty'] == specialty]
        if city:
            df = df[df['city'] == city]
        if contacted is not None:
            df = df[df['contacted'] == contacted]
        return df.head(10).to_dict(orient='records') if not df.empty else "No HCPs found."

    def _create_agent(self):
        tool_names = [tool.name for tool in self.tools]
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are Nova, a specialized AI assistant for pharmaceutical sales and marketing teams.
            You help users discover healthcare professionals (HCPs), research relevant medical content, and generate personalized outreach materials.

            The available tool names are: {tool_names}

            Available tools:
            {tools}
            """),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]).partial(tool_names=tool_names, tools=self.tools)
        return create_json_chat_agent(llm=self.llm, tools=self.tools, prompt=prompt)

    def run(self, query):
        return self.agent_executor.invoke({"input": query})["output"]


def main():
    print("Initializing Nova, your pharmaceutical outreach assistant...")
    nova = NovaAgent()

    print("\n==== Nova is ready to help you engage with healthcare professionals ====")
    print("Type 'exit' to end the conversation.")

    while True:
        user_input = input("\nYou: ")
        if user_input.lower() in ['exit', 'quit', 'bye']:
            print("\nNova: Thank you for using Nova! Goodbye.")
            break

        try:
            response = nova.run(user_input)
            print(f"\nNova: {response}")
        except Exception as e:
            print(f"\nNova: I apologize, but I encountered an error: {str(e)}")
            print("Let's try a different approach. How else can I help you today?")

if __name__ == "__main__":
    main()
