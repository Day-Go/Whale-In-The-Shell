import random
import openai
import logging
from supabase import Client

from llm import LLM
from data_access_object import DataAccessObject
from models.enums import Event, SENTIMENT
from generators import OrgGenerator, AgentGenerator

logging.basicConfig(level=logging.INFO)

ANNOUNCEMENT_PROBABILITY_START = 100
ANNOUNCEMENT_PROBABILITY_END = 5
MAX_STEP_COUNT = 1000

class GameMaster(LLM):
    def __init__(
            self, 
            api_key: str, 
            dao: DataAccessObject, 
            org_generator: OrgGenerator, 
            agent_generator: AgentGenerator
        ):
        super().__init__(api_key)
        self.dao = dao
        self.org_generator = org_generator
        self.agent_generator = agent_generator
        self.step_count = 0

        self.system_prompt =  self.dao.get_prompt_by_name('GM_SystemPrompt')

    def get_event_type(self) -> Event:
        probability = self.calculate_announcement_probability(self.step_count)
        return Event.ANNOUNCEMENT if random.random() * 100 < probability else Event.DEVELOPMENT

    def get_event_sentiment(self) -> SENTIMENT:
        return SENTIMENT.NEGATIVE

    @staticmethod
    def calculate_announcement_probability(step_count: int) -> float:
        # Refactored calculation into a static method
        return max(
            ANNOUNCEMENT_PROBABILITY_END,
            ANNOUNCEMENT_PROBABILITY_START - ((ANNOUNCEMENT_PROBABILITY_START - ANNOUNCEMENT_PROBABILITY_END) * step_count / MAX_STEP_COUNT)
        )
    
    def timestep(self) -> None:
        event_type = self.get_event_type()
        self.process_event(event_type)
        self.step_count += 1

    def process_event(self, event_type: Event) -> None:
        if event_type == Event.ANNOUNCEMENT:
            self.generate_announcement()
            self.generate_update()
            self.generate_development()
            
        else:
            self.generate_development()

    def generate_announcement(self):
        new_org = self.org_generator.create()
        logging.info(f"Created new organisation with id {new_org['id']}")

        new_product = self.org_generator.create_new_product(
            org_id=new_org['id'], 
            org_type=new_org['type'], 
            org_name=new_org['name']
        )
        logging.info(f"Created new product with id {new_product['id']}")

        message = self.build_announcement_message(new_org, new_product)

        self.prompt_and_save(message, Event.ANNOUNCEMENT, new_org, new_product)

    def generate_development(self):
        # 1. Get random event from database
        event = self.dao.get_random_recent_event(12)
        logging.info(f"Retrieved event: {event}")

        # 2. Get linked organisation and product (probably not needed)
        organisation = self.dao.get_org_by_event_id(event['id'])
        product = self.dao.get_product_by_event_id(event['id'])

        # 3. Choose sentiment for the development
        sentiment = self.get_event_sentiment()

        # 4. Generate development that follows from the event
        message = self.build_development_message(
            event, 
            organisation, 
            product,
            sentiment.name
        )

        self.prompt_and_save(message, Event.DEVELOPMENT, organisation, product)

    def generate_update(self):
        event = self.dao.get_random_recent_event_by_type(Event.ANNOUNCEMENT.value, 12)

        organisation = self.dao.get_org_by_event_id(event['id'])
        product = self.dao.get_product_by_event_id(event['id'])

        message = self.build_update_message(
            event, 
            organisation, 
            product,
        )
        
        self.prompt_and_save(message, Event.UPDATE, organisation, product)

    def build_announcement_message(self, new_org: dict, new_product: dict):
        prompt = self.dao.get_prompt_by_name('GM_Announcement')
        prompt = prompt.format(
            event='launch announcement', 
            product=new_product['name'], 
            org=new_org['name']
        )
        logging.info(f"Prompt: {prompt}")

        return [{"role": "system", "content": self.system_prompt}, 
                {"role": "user", "content": prompt}]

    def build_development_message(self, prev_event: dict, organisation: dict, product: dict, sentiment: str):
        prompt = self.dao.get_prompt_by_name('GM_Development')
        prompt = prompt.format(
            event=prev_event['event_details'], 
            org=organisation['name'],
            product=product['name'], 
            sentiment=sentiment
        )

        logging.info(f"Prompt: {prompt}")

        return [{"role": "system", "content": self.system_prompt}, 
                {"role": "user", "content": prompt}]

    def build_update_message(self, prev_event: dict, organisation: dict, product: dict):
        prompt = self.dao.get_prompt_by_name('GM_Update')
        prompt = prompt.format(
            event=prev_event['event_details'], 
            org=organisation['name'],
            product=product['name'], 
        )

        logging.info(f"Prompt: {prompt}")

        return [{"role": "system", "content": self.system_prompt}, 
                {"role": "user", "content": prompt}]

    def prompt_and_save(self, message: str, event_type: Event, organisation: dict, product: dict):
        event = self.chat(message, temp=1.25, max_tokens=80)
        event_embedding = self.generate_embedding(event)
        logging.info(f"Generated announcement: {event}")

        event_row = self.dao.insert(
            'events',
            event_type=event_type.value, 
            event_details=event, 
            embedding=event_embedding
        )

        self.dao.insert(
            'eventsorganisations',
            event_id=event_row.data[0]['id'],
            org_id=organisation['id']
        )

        self.dao.insert(
            'eventsproducts',
            event_id=event_row.data[0]['id'],
            product_id=product['id']
        )

