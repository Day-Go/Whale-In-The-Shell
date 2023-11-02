import re
import openai
import logging
from supabase import Client

from llm import LLM
from data_access_object import DataAccessObject

logging.basicConfig(level=logging.INFO)

class Agent(LLM):
    def __init__(self, agent_id: int, api_key: str, dao: DataAccessObject):
        super().__init__(api_key)
        self.id = agent_id
        self.dao = dao

        self.get_agent_information()
        self.set_system_prompt()
        self.message_history = [{"role": "system", "content": f"{self.system_prompt}"}]

    def get_agent_information(self) -> None:
        response = self.dao.get_agent_by_id(self.id)
        self.agent_name = response.data[0]['name']
        self.biography = response.data[0]['biography']

    def set_system_prompt(self) -> None:
        prompt_name = 'AgentSystemPrompt'
        prompt = self.dao.get_prompt_by_name(prompt_name)

        self.system_prompt = prompt.format(name=self.agent_name, biography=self.biography)
        logging.info(f'System prompt: {self.system_prompt}')

    def observe(self):
        event = self.dao.get_random_recent_event(time_delta_minutes=10000)
        if not event:
            logging.warning("No recent events found.")
            return None
    
        event_id = event['id']
        event_details = event['event_details']
        logging.info(f'Event observed: {event}')

        prompt_name = 'AgentObserve'
        prompt = self.dao.get_prompt_by_name(prompt_name)

        # TODO: Proper exception handling
        if prompt:
            prompt = prompt.format(name=self.agent_name, event=event_details)
            logging.info(f"Formatted prompt: {prompt}")

            message = self.message_history + [{"role": "user", "content": f"{prompt}"}]
            reply_content = self.chat(message)
            logging.info(f"Reply from OpenAI: {reply_content}")
        else:
            logging.warning(f"Prompt {prompt_name} not found or could not be formatted.")
            reply_content = None

        self.insert_memory(reply_content, event_id)

        return reply_content

    def reflect(self):
        pass

    def plan(self):
        pass

    def insert_memory(self, response: str, event_id: int):
        # Responses can be cut off mid sentence due to token limit.
        # Use a regular expression to match complete sentences
        matches = re.findall(r'\s*[^.!?]*[.!?]', response)
        complete_paragraph = ''.join(matches).strip()

        embedding = self.generate_embedding(complete_paragraph)

        data = {
            'agent_id': self.id,
            'memory_details': complete_paragraph,
            'embedding': embedding
        }
        
        db_response = self.dao.insert_memory(data)
        if db_response.data:
            memory_event_data = {
                'memory_id': db_response.data[0]['id'],
                'event_id': event_id   
            }
            self.dao.insert_memory_event_assosciation(memory_event_data)
        else:
            # Handle the case where the memory wasn't inserted properly
            logging.error("Failed to insert memory.")