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

    def update(self, table_name: str, id: int, **kwargs) -> Any:
        try:
            data = kwargs
            return self.sb_client.table(table_name).update(data).eq('id', id).execute()
        except Exception as e:
            logging.error(f"An error occurred during update operation on {table_name}: {e}")
            return None

    def get_agent_by_id(self, agent_id: int):
        columns = ('name, biography, occupation, handle, nationality, balance, '
                   'investment_style, risk_tolerance, communication_style')
        response = self.sb_client.table('agents') \
                                 .select(columns) \
                                 .eq('id', agent_id) \
                                 .execute()
        return response.data[0]

    def get_agent_wallet_by_id(self, agent_id: int) -> dict:
        response = self.sb_client.table('wallet') \
                                 .select('balance, asset_id') \
                                 .eq('agent_id', agent_id) \
                                 .execute()
        
        return response.data

    def get_asset_by_id(self, currency_id: int) -> str:
        response = self.sb_client.table('asset') \
                                 .select('name, ticker') \
                                 .eq('id', currency_id) \
                                 .execute()
        
        return response.data[0]

    def get_asset_by_name(self, currency_name: str) -> str:
        response = self.sb_client.table('assets') \
                                 .select('*') \
                                 .eq('name', currency_name) \
                                 .execute()
        
        return response.data[0]

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
        
        return random.choice(response.data)['name']

    def get_crypto_product_by_id(self, id: int) -> str:
        response = self.sb_client.table('crypto_products') \
                                 .select('id, name') \
                                 .eq('id', id) \
                                 .execute()
        return response.data[0]
    
    def get_random_crypto_product(self) -> str:
        response = self.sb_client.table("id, crypto_products") \
                                 .select("id, name", count="exact") \
                                 .execute()
        
        return random.choice(response.data)
    
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

    def get_event_by_id(self, event_id: int) -> str:
        response = self.sb_client.table('events')\
            .select('id, event_details, created_at, embedding, event_type')\
            .eq('id', event_id)\
            .execute()

        return response.data[0]
    
    def get_random_event(self):
        response = self.sb_client.table('events')\
            .select('id, event_details')\
            .execute()

        random_event = random.choice(response.data) if response.data else None
        return random_event

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
            .select('id, name, type')\
            .eq('id', product_id.data[0]['product_id'])\
            .execute()

        return response.data[0] if response.data else None
    
    def get_random_nationality(self) -> str:
        nationalities = self.sb_client.table('nationalities')\
            .select('id, name', count="exact")\
            .execute()
        
        return random.choice(nationalities.data)['name']

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
        
        return random.choice(occupations.data)['name']

    def get_occupation_by_id(self, occupation_id: int) -> str:
        occupation = self.sb_client.table('occupations')\
            .select('id, name')\
            .eq('id', occupation_id)\
            .execute()
        
        return occupation.data[0]['name'] if occupation.data else None
    
    def get_n_random_traits(self, n: int) -> list:
        traits = self.sb_client.table('traits')\
            .select('id, trait, anti_trait', count="exact")\
            .execute()
        
        sampled_rows = random.sample(traits.data, n)
        
        random_traits = []
        for row in sampled_rows:
            is_positive = random.random() < 0.5
            chosen_trait = row['trait'] if is_positive else row['anti_trait']
            random_traits.append({'id': row['id'], 'trait': chosen_trait, 'is_positive': is_positive})
        
        return random_traits

    def get_random_investment_style(self) -> str:
        trading_styles = self.sb_client.table('investment_styles')\
            .select('id, style', count="exact")\
            .execute()
        
        return random.choice(trading_styles.data)['style']

    def get_random_risk_tolerance(self) -> str:
        risk_tolerances = self.sb_client.table('risktolerances')\
            .select('id, tolerance_level', count="exact")\
            .execute()
        
        return random.choice(risk_tolerances.data)['tolerance_level']

    def get_random_communication_style(self) -> str:
        communication_styles = self.sb_client.table('communication_styles')\
            .select('id, style', count="exact")\
            .execute()
        
        return random.choice(communication_styles.data)['style']