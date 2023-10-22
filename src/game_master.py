import os
import openai
import json
import logging
from supabase import Client

logging.basicConfig(level=logging.INFO)

class GameMaster:
    def __init__(self, api_key: str, supabase: Client):
        openai.api_key = api_key
        self.supabase = supabase

        self.set_system_prompt()
        self.message_history = [{"role": "system", "content": f"{self.system_prompt}"}]

    def get_prompt_by_name_from_supabase(self, prompt_name: str) -> str:
        retrieved_data = self.supabase.table("prompts").select("content").eq('name', prompt_name).execute()

        # TODO: Proper exception handling
        if retrieved_data.data:
            prompt = retrieved_data.data[0]['content']
            logging.info(f"Retrieved prompt with name {prompt_name}: {prompt}")
        else:
            prompt = None
            logging.info(f"Retrieved prompt with name {prompt_name}: {prompt}")

        return prompt

    def set_system_prompt(self):
        prompt_name = 'GameMasterSystemPrompt'
        self.system_prompt = self.get_prompt_by_name_from_supabase(prompt_name)

        logging.info(f"System prompt: {self.system_prompt}")

    def generate_announcement(self, entity, product, sentiment):
        prompt_name = 'GameMasterAnnouncement'
        prompt = self.get_prompt_by_name_from_supabase(prompt_name)
        prompt = prompt.format(entity=entity, product=product, sentiment=sentiment)
        logging.info(f"Formatted prompt: {prompt}")

        message = self.message_history + [{"role": "user", "content": f"{prompt}"}]     

        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=message
        )

        reply_content = completion.choices[0].message.content
        logging.info(f"Reply from OpenAI: {reply_content}")


    def generate_event(self, entity, product, sentiment):
        prompt_name = 'GameMasterEvent'
        prompt = self.get_prompt_by_name_from_supabase(prompt_name)
        prompt = prompt.format(entity=entity, product=product, sentiment=sentiment)
        logging.info(f"Formatted prompt: {prompt}")

        message = self.message_history + [{"role": "user", "content": f"{prompt}"}]     

        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=message
        )

        reply_content = completion.choices[0].message.content
        logging.info(f"Reply from OpenAI: {reply_content}")