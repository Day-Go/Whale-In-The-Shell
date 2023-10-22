import openai
import logging
from supabase import Client

from llm import LLM

logging.basicConfig(level=logging.INFO)

class Agent(LLM):
    def __init__(self, api_key: str, supabase: Client, id: int):
        super.__init__(api_key, supabase)

        self.id = id
        self.get_agent_information()

    def get_agent_information(self) -> None:
        response = self.supabase.table('agents').select('name, biography').eq('id', id).execute()
        self.agent_name = response['data'][0]['name']
        self.biography = response['data'][0]['biography']

    def set_system_prompt(self) -> None:
        prompt_name = 'AgentSystemPrompt'
        prompt = self.get_prompt_by_name_from_supabase(prompt_name)

        logging.info(f'System prompt: {self.system_prompt}')