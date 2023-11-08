import random
import logging
from typing import Any
from datetime import datetime, timedelta
from supabase import Client

class DataAccessObject:
    def __init__(self, client: Client):
        self.sb_client = client

    def insert(self, table_name: str, **kwargs) -> Any:
        try:
            data = kwargs
            return self.sb_client.table(table_name).insert(data).execute()
        except Exception as e:
            logging.error(f"An error occurred during insert operation on {table_name}: {e}")
            return None

    def get_agent_by_id(self, agent_id):
        response = self.sb_client.table('agents') \
                                 .select('name, biography') \
                                 .eq('id', agent_id) \
                                 .execute()
        return response.data

    def get_org_type_by_id(self, id: int) -> str:
        response = self.sb_client.table('organisation_types') \
                                 .select('name') \
                                 .eq('id', id) \
                                 .execute()
        return response.data[0]['name']
    
    def get_random_org_type(self) -> str:
        response = self.sb_client.table("org_types") \
                                 .select("id, name", count="exact") \
                                 .execute()
        
        idx = random.randint(1,response.count)
        return response.data[idx]['name']

    def get_crypto_product_by_id(self, id: int) -> str:
        response = self.sb_client.table('crypto_products') \
                                 .select('name') \
                                 .eq('id', id) \
                                 .execute()
        return response.data[0]['name']
    
    def get_random_crypto_product(self) -> str:
        response = self.sb_client.table("crypto_products") \
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
        
    def get_random_recent_event(self, time_delta_hours: int):
        now = datetime.now()
        one_hour_ago = now - timedelta(hours=time_delta_hours)

        response = self.sb_client.table('events')\
            .select('id, event_details')\
            .gte('created_at', one_hour_ago)\
            .order('created_at')\
            .execute()

        random_event = random.choice(response.data) if response.data else None
        return random_event
    
    def get_random_recent_event_by_type(self, event_type: str, time_delta_hours: int):
        now = datetime.now()
        one_hour_ago = now - timedelta(hours=time_delta_hours)

        response = self.sb_client.table('events')\
            .select('id, event_details')\
            .eq('event_type', event_type)\
            .gte('created_at', one_hour_ago)\
            .order('created_at')\
            .execute()

        random_event = random.choice(response.data) if response.data else None
        return random_event

    def get_org_by_event_id(self, event_id: int) -> str:
        org_id = self.sb_client.table('eventsorganisations')\
            .select('org_id')\
            .eq('event_id', event_id)\
            .execute()
        logging.info(f"Retrieved organisation id: {org_id}")

        response = self.sb_client.table('organisations')\
            .select('id, name')\
            .eq('id', org_id.data[0]['org_id'])\
            .execute()

        return response.data[0] if response.data else None
    
    def get_product_by_event_id(self, event_id: int) -> str:
        product_id = self.sb_client.table('eventsproducts')\
            .select('product_id')\
            .eq('event_id', event_id)\
            .execute()
        
        response = self.sb_client.table('products')\
            .select('id, name')\
            .eq('id', product_id.data[0]['product_id'])\
            .execute()

        return response.data[0] if response.data else None
    
    def get_random_nationality(self) -> str:
        nationalities = self.sb_client.table('nationalities')\
            .select('id, name', count="exact")\
            .execute()
        
        idx = random.randint(1, nationalities.count)
        return nationalities.data[idx]['name']

    def get_nationality_by_id(self, nationality_id: int) -> str:
        nationality = self.sb_client.table('nationalities')\
            .select('id, name')\
            .eq('id', nationality_id)\
            .execute()
        
        return nationality.data[0]['name'] if nationality.data else None

    def get_random_occupation(self) -> str:
        occupations = self.sb_client.table('occupations')\
            .select('id, name', count="exact")\
            .execute()
        
        idx = random.randint(1, occupations.count)
        return occupations.data[idx]['name']

    def get_occupation_by_id(self, occupation_id: int) -> str:
        occupation = self.sb_client.table('occupations')\
            .select('id, name')\
            .eq('id', occupation_id)\
            .execute()
        
        return occupation.data[0]['name'] if occupation.data else None