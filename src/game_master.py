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

    def set_system_prompt(self) -> None:
        prompt_name = 'GameMasterSystemPrompt'
        self.system_prompt = self.get_prompt_by_name_from_supabase(prompt_name)

        logging.info(f"System prompt: {self.system_prompt}")

    def generate_message(self, entity: str, product: str, sentiment: str, message_type: str) -> str:
        if message_type == "announcement":
            prompt_name = 'GameMasterAnnouncement'
        elif message_type == "event":
            prompt_name = 'GameMasterEvent'
        else:
            logging.error(f"Invalid message type: {message_type}")
            return

        prompt = self.get_prompt_by_name_from_supabase(prompt_name)

        # TODO: Proper exception handling
        if prompt:
            prompt = prompt.format(entity=entity, product=product, sentiment=sentiment)
            logging.info(f"Formatted prompt: {prompt}")

            message = self.message_history + [{"role": "user", "content": f"{prompt}"}]

            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=message
            )

            reply_content = completion.choices[0].message['content']  # Adjusted to access 'content' key
            logging.info(f"Reply from OpenAI: {reply_content}")
        else:
            reply_content = None
            logging.warning(f"Prompt {prompt_name} not found or could not be formatted")

        return reply_content

