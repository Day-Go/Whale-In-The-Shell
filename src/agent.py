import re
import openai
import logging
from supabase import Client


from llm import LLM

logging.basicConfig(level=logging.INFO)

class Agent(LLM):
    def __init__(self, api_key: str, supabase: Client, agent_id: int):
        super().__init__(api_key, supabase)

        self.id = agent_id
        self.get_agent_information()
        self.set_system_prompt()
        self.message_history = [{"role": "system", "content": f"{self.system_prompt}"}]

    def get_agent_information(self) -> None:
        response = self.supabase.table('agents').select('name, biography').eq('id', self.id).execute()
        self.agent_name = response.data[0]['name']
        self.biography = response.data[0]['biography']

    def set_system_prompt(self) -> None:
        prompt_name = 'AgentSystemPrompt'
        prompt = self.get_prompt_by_name_from_supabase(prompt_name)

        self.system_prompt = prompt.format(name=self.agent_name, biography=self.biography)
        logging.info(f'System prompt: {self.system_prompt}')

    def observe(self):
        event = self.get_random_recent_event(time_delta_minutes=10000)
        event_id = event['id']
        event_details = event['event_details']
        logging.info(f'Event observed: {event}')

        prompt_name = 'AgentObserve'
        prompt = self.get_prompt_by_name_from_supabase(prompt_name)

        # TODO: Proper exception handling
        if prompt:
            prompt = prompt.format(name=self.agent_name, event=event_details)
            logging.info(f"Formatted prompt: {prompt}")

            message = self.message_history + [{"role": "user", "content": f"{prompt}"}]

            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=message,
                temperature=1.2,
                max_tokens=80
            )

            reply_content = completion.choices[0].message['content']  # Adjusted to access 'content' key
            logging.info(f"Reply from OpenAI: {reply_content}")
        else:
            reply_content = None
            logging.warning(f"Prompt {prompt_name} not found or could not be formatted")

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

        response_embedding = openai.Embedding.create(
            input=complete_paragraph,
            model='text-embedding-ada-002'
        )

        embedding = response_embedding['data'][0]['embedding']

        data = {
            'agent_id': self.id,
            'memory_details': complete_paragraph,
            'embedding': embedding
        }
        db_response = self.supabase.table('memories').insert(data).execute()


        join_data = {
            'memory_id': db_response.data[0]['id'],
            'event_id': event_id   
        }
        self.supabase.table('memoryeventassociations').insert(join_data).execute()