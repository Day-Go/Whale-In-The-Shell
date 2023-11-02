import openai
import logging
from supabase import Client

from llm import LLM
from data_access_object import DataAccessObject
from models.enums import Event

logging.basicConfig(level=logging.INFO)

class GameMaster(LLM):
    def __init__(self, api_key: str, dao: DataAccessObject):
        super().__init__(api_key)
        self.dao = dao

        self.set_system_prompt()
        self.message_history = [{"role": "system", "content": f"{self.system_prompt}"}]

    def set_system_prompt(self) -> None:
        prompt_name = 'GameMasterSystemPrompt'
        self.system_prompt = self.dao.get_prompt_by_name(prompt_name)

        logging.info(f"System prompt: {self.system_prompt}")

    def generate_message(self, entity: str, product: str, sentiment: str, event: Event) -> str:
        # TODO: Make an event_type enum
        if event == Event.ANNOUNCEMENT:
            prompt_name = 'GameMasterAnnouncement'
        elif event == Event.DEVELOPMENT:
            prompt_name = 'GameMasterDevelopment'
        else:
            logging.error(f"Invalid message type: {event}")
            return

        prompt = self.dao.get_prompt_by_name(prompt_name)

        # TODO: Proper exception handling
        if prompt:
            prompt = prompt.format(entity=entity, product=product, sentiment=sentiment)
            logging.info(f"Formatted prompt: {prompt}")

            message = self.message_history + [{"role": "user", "content": f"{prompt}"}]

            reply_content = self.chat(message)
            logging.info(f"Reply from OpenAI: {reply_content}")
        else:
            reply_content = None
            logging.warning(f"Prompt {prompt_name} not found or could not be formatted")

        return reply_content

