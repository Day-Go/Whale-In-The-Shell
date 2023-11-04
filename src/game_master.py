import random
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
        self.step_count = 0

        self.get_system_prompt()
        self.message_history = [{"role": "system", "content": f"{self.system_prompt}"}]

    def get_system_prompt(self) -> None:
        prompt_name = 'GM_SystemPrompt'
        self.system_prompt = self.dao.get_prompt_by_name(prompt_name)

    def timestep(self):
        """
        Executes a single timestep in the game, where an event is randomly chosen and
        processed. The type of event is dependent on the step_count of the game, with
        announcements becoming less likely and developments more likely as time progresses.
        """
        # Calculate the probability of the event being an announcement, which decreases
        # as the step_count increases, from 100% at step_count=0 to 5% at step_count=1000.
        # NOTE: This implementation only works for 2 event types and will need to be changed.
        announcement_probability = max(5, 100 - (95 * self.step_count / 1000))
        event_type = Event.ANNOUNCEMENT if random.random() * 100 < announcement_probability else Event.DEVELOPMENT

        if event_type == Event.ANNOUNCEMENT:
            self.generate_announcement()
        else:
            self.generate_development()

        self.step_count += 1


    def generate_announcement(self):
        prompt_name = 'prompt_name'
        prompt = self.dao.get_prompt_by_name(prompt_name) 

        
    def generate_development():
        pass

    def create_new_entity(self):
        crypto_company_id = 2
        entity_type = self.dao.get_entity_type_by_id(crypto_company_id)

        entity_name = self.generate_entity_name(entity_type)
        entity_mission = self.generate_entity_mission_statement(entity_type, entity_name)
        entity_desc = self.generate_entity_description(entity_type, entity_name, entity_mission)

        self.dao.insert_entity(name=entity_name, 
                               type=entity_type, 
                               description=entity_desc, 
                               mission=entity_mission)

    def generate_entity_name(self, entity_type: str) -> str:
        prompt = self.dao.get_prompt_by_name('GM_GenEntityName')
        prompt = prompt.format(entity_type=entity_type)
        message = [{"role": "user", "content": f"{prompt}"}]
        logging.info(f"Prompt: {prompt}")

        entity_name = self.chat(message, 1.2, 8)
        logging.info(f"Entity name: {entity_name}")

        return entity_name

    def generate_entity_mission_statement(self, entity_type: str, entity_name: str) -> str:
        prompt = self.dao.get_prompt_by_name('GM_GenEntityMission')
        prompt = prompt.format(entity_type=entity_type, 
                               entity_name=entity_name)
        message = [{"role": "user", "content": f"{prompt}"}]
        logging.info(f"Prompt: {prompt}")

        entity_mission = self.chat(message, 1.2, 80)
        logging.info(f"Entity mission statement: {entity_mission}")

        return entity_mission

    def generate_entity_description(self, entity_type: str, entity_name:str, entity_mission: str) -> str:
        prompt = self.dao.get_prompt_by_name('GM_GenEntityDesc')
        prompt = prompt.format(entity_type=entity_type, entity_name=entity_name,entity_mission=entity_mission)
        message = [{"role": "user", "content": f"{prompt}"}]
        logging.info(f"Prompt: {prompt}")

        entity_desc = self.chat(message, 1.2, 80)
        logging.info(f"Entity description: {entity_desc}")

        return entity_desc


    def generate_message(self, entity: str, product: str, sentiment: str, event_type: Event) -> None:
        prompt = self.get_prompt(event_type)
        prompt = prompt.format(entity=entity, product=product, sentiment=sentiment)
        logging.info(f"Formatted prompt: {prompt}")

        message = self.message_history + [{"role": "user", "content": f"{prompt}"}]

        response = self.chat(message)
        embedding = self.generate_embedding(response)

        data = {
            'event_type': event_type,
            'event_details': response,
            'embedding': embedding
        }

    def get_prompt(self, event: Event) -> str:
        prompt_names = {
            Event.ANNOUNCEMENT: 'GM_Announcement',
            Event.DEVELOPMENT: 'GameMasterDevelopment',
        }
        
        prompt_name = prompt_names.get(event)
        if prompt_name is None:
            logging.error(f"Invalid message type: {event}")
            return None 
        
        return self.dao.get_prompt_by_name(prompt_name) 

