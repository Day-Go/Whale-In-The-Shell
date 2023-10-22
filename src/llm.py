import openai
import logging
from supabase import Client

class LLM:
    def __init__(self, api_key: str, supabase: Client):
        openai.api_key = api_key
        self.supabase = supabase

    def get_prompt_by_name_from_supabase(self, prompt_name: str) -> str:
        retrieved_data = self.supabase.table('prompts').select('content').eq('name', prompt_name).execute()

        # TODO: Proper exception handling
        if retrieved_data.data:
            prompt = retrieved_data.data[0]['content']
            logging.info(f'Retrieved prompt with name {prompt_name}: {prompt}')
        else:
            prompt = None
            logging.info(f'Retrieved prompt with name {prompt_name}: {prompt}')

        return prompt