import random
import logging
from datetime import datetime, timedelta
from supabase import Client

class DataAccessObject:
    def __init__(self, client: Client):
        self.sb_client = client

    def insert_event(self, data):
        return self.sb_client.table('memories').insert(data).execute()
    
    def insert_memory(self, data):
        return self.sb_client.table('events').insert(data).execute()
    
    def insert_memory_event_assosciation(self, data):
        return self.sb_client.table('memoryeventassociations').insert(data).execute()

    def insert_entity(self, name: str, type: str, description: str, mission: str):
        data = {
            'name': name,
            'type': type,
            'description': description,
            'mission': mission
        }

        return self.sb_client.table('entities').insert(data).execute()


    def get_agent_by_id(self, agent_id):
        response = self.sb_client.table('agents') \
                                 .select('name, biography') \
                                 .eq('id', agent_id) \
                                 .execute()
        return response.data

    def get_entity_type_by_id(self, id: int) -> str:
        response = self.sb_client.table('entity_types') \
                                 .select('name') \
                                 .eq('id', id) \
                                 .execute()
        return response.data[0]['name']
    
    def get_random_entity_type(self) -> str:
        response = self.sb_client.table("entity_types") \
                                 .select("id, name", count="exact") \
                                 .execute()
        
        idx = random.randint(1,response.count)
        return response.data[idx]['name']


    def get_prompt_by_name(self, prompt_name: str) -> str:
        try:
            response = self.sb_client.table('prompts').select('content').eq('name', prompt_name).execute()

            if response.data:
                prompt = response.data[0]['content']
                return prompt
            else:
                logging.warning(f'Prompt with name {prompt_name} not found.')
                return None
        except Exception as e:
            logging.error(f"An error occurred while retrieving the prompt: {e}")
            return None
        

    def get_random_recent_event(self, time_delta_minutes: int):
        now = datetime.now()
        one_hour_ago = now - timedelta(minutes=time_delta_minutes)

        response = self.sb_client.table('events')\
            .select('id, event_details')\
            .gte('created_at', one_hour_ago)\
            .order('created_at')\
            .execute()

        random_event = random.choice(response.data) if response.data else None
        return random_event