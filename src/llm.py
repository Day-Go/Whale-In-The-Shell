import random
import openai
import logging
from supabase import Client
from datetime import datetime, timedelta

class LLM:
    def __init__(self, api_key: str, supabase: Client):
        openai.api_key = api_key
        self.supabase = supabase

    def get_prompt_by_name_from_supabase(self, prompt_name: str) -> str:
        response = self.supabase.table('prompts').select('content').eq('name', prompt_name).execute()

        # TODO: Proper exception handling
        if response.data:
            prompt = response.data[0]['content']
            logging.info(f'Retrieved prompt with name {prompt_name}: {prompt}')
        else:
            prompt = None
            logging.info(f'Retrieved prompt with name {prompt_name}: {prompt}')

        return prompt
    
    def get_random_recent_event(self, time_delta_minutes: int):
        now = datetime.now()
        one_hour_ago = now - timedelta(minutes=time_delta_minutes)

        response = self.supabase.table('events')\
            .select('id, event_details')\
            .gte('created_at', one_hour_ago)\
            .order('created_at')\
            .execute()

        random_event = random.choice(response.data) if response.data else None
        return random_event