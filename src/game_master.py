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

        self.get_system_prompt()
        self.message_history = [{"role": "system", "content": f"{self.system_prompt}"}]

    def get_system_prompt(self):
        prompt_name = 'GameMasterSystemPrompt'
        retrieved_data = self.supabase.table("prompts").select("content").eq('name', prompt_name).execute()

        if retrieved_data.data:
            self.system_prompt = retrieved_data.data[0]['content']
        else:
            self.system_prompt = None
            print(f"No prompt found with name {prompt_name}")

    def generate_scenario(self, asset, entity, sentiment):
        message = self.message_history.copy()
        message.append({"role": "user", "content": f"Generate a {sentiment} scenario about the product {asset}, created by {entity}. Scenario:"})
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=message
        )

        reply_content = completion.choices[0].message.content

        response = reply_content

     