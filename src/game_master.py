import random
import openai
import logging
from supabase import Client

from llm import LLM
from data_access_object import DataAccessObject
from models.enums import Event, SENTIMENT

logging.basicConfig(level=logging.INFO)

ANNOUNCEMENT_PROBABILITY_START = 100
ANNOUNCEMENT_PROBABILITY_END = 5
MAX_STEP_COUNT = 1000

class GameMaster(LLM):
    def __init__(self, api_key: str, dao: DataAccessObject):
        super().__init__(api_key)
        self.dao = dao
        self.step_count = 0

    def get_event_type(self) -> Event:
        probability = self.calculate_announcement_probability(self.step_count)
        return Event.ANNOUNCEMENT if random.random() * 100 < probability else Event.DEVELOPMENT

    def get_event_sentiment(self) -> SENTIMENT:
        return SENTIMENT.NEUTRAL

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
            # self.generate_announcement()
            self.generate_development()
        else:
            self.generate_development()

    def generate_announcement(self):
        new_entity = self.create_new_entity()
        logging.info(f"Created new entity with id {new_entity['id']}")

        new_product = self.create_new_product(
            entity_id=new_entity['id'], 
            entity_type=new_entity['type'], 
            entity_name=new_entity['name']
        )
        logging.info(f"Created new product with id {new_product['id']}")

        message = self.build_announcement_message(new_entity, new_product)

        self.prompt_and_save(message, Event.ANNOUNCEMENT, new_entity, new_product)

    def generate_development(self):
        # 1. Get random event from database
        event = self.dao.get_random_recent_event(1000)
        logging.info(f"Retrieved event: {event}")

        # 2. Get linked entity and product (probably not needed)
        entity = self.dao.get_entity_by_event_id(event['id'])
        product = self.dao.get_product_by_event_id(event['id'])

        # 3. Choose sentiment for the development
        sentiment = self.get_event_sentiment()

        # 4. Generate development that follows from the event
        message = self.build_development_message(
            event, 
            entity, 
            product,
            sentiment.name
        )

        self.prompt_and_save(message, Event.ANNOUNCEMENT, entity, product)

    def build_announcement_message(self, new_entity: dict, new_product: dict):
        system_prompt =  self.dao.get_prompt_by_name('GM_SystemPrompt')
        prompt = self.dao.get_prompt_by_name('GM_Announcement')
        prompt = prompt.format(
            event='launch announcement', 
            product=new_product['name'], 
            entity=new_entity['name']
        )
        logging.info(f"Prompt: {prompt}")

        return [{"role": "system", "content": system_prompt}, 
                {"role": "user", "content": prompt}]

    def build_development_message(self, prev_event: dict, entity: dict, product: dict, sentiment: str):
        system_prompt =  self.dao.get_prompt_by_name('GM_SystemPrompt')
        prompt = self.dao.get_prompt_by_name('GM_Development')
        prompt = prompt.format(
            event=prev_event['event_details'], 
            entity=entity['name'],
            product=product['name'], 
            sentiment=sentiment
        )

        logging.info(f"Prompt: {prompt}")

        return [{"role": "system", "content": system_prompt}, 
                {"role": "user", "content": prompt}]

    def prompt_and_save(self, message: str, event_type: Event, entity: dict, product: dict):
        event = self.chat(message, temp=1.2, max_tokens=80)
        event_embedding = self.generate_embedding(event)
        logging.info(f"Generated announcement: {event}")

        event_row = self.dao.insert(
            'events',
            event_type=event_type.value, 
            event_details=event, 
            embedding=event_embedding
        )

        self.dao.insert(
            'eventsentities',
            event_id=event_row.data[0]['id'],
            entity_id=entity['id']
        )

        self.dao.insert(
            'eventsproducts',
            event_id=event_row.data[0]['id'],
            product_id=product['id']
        )


    def create_new_entity(self):
        try:
            entity_type = self.dao.get_entity_type_by_id(2)
            entity_name = self.generate_entity_attribute(
                'GM_GenEntityName', entity_type=entity_type
            )
            entity_mission = self.generate_entity_attribute(
                'GM_GenEntityMission', entity_type=entity_type, entity_name=entity_name
            )
            entity_desc = self.generate_entity_attribute(
                'GM_GenEntityDesc', entity_type=entity_type, 
                entity_name=entity_name, entity_mission=entity_mission
            )

            response = self.dao.insert(
                'entities',
                name=entity_name,
                type=entity_type,
                description=entity_desc,
                mission=entity_mission
            )

            return response.data[0]
        except Exception as e:
            # Properly handle exceptions and log the error
            logging.error(f"Failed to create new entity: {e}")
            raise

    def generate_entity_attribute(self, prompt_name: str, **kwargs) -> str:
        prompt = self.dao.get_prompt_by_name(prompt_name).format(**kwargs)
        message = [{"role": "user", "content": prompt}]
        logging.info(f"Prompt: {prompt}")

        entity_attribute = self.chat(message, 1.25, 80)
        logging.info(f"Generated attribute: {entity_attribute}")

        if not entity_attribute:
            raise ValueError(f"Failed to generate entity attribute with prompt: {prompt}")

        return entity_attribute

    def create_new_product(self, **kwargs) -> str:
        product_type = self.dao.get_random_crypto_product()
        product_name = self.generate_product_name(
            entity_type=kwargs.get('entity_type'), 
            entity_name=kwargs.get('entity_name'), 
            product_type=product_type
        )

        response = self.dao.insert(
            'products',
            entity_id=kwargs.get('entity_id'), 
            name=product_name
        )

        return response.data[0]

    def generate_product_name(self, **kwargs) -> str:
        entity_type = kwargs.get('entity_type')
        entity_name = kwargs.get('entity_name')
        product_type = kwargs.get('product_type')

        prompt = self.dao.get_prompt_by_name('GM_GenProductName').format(
            entity_type=entity_type, entity_name=entity_name, product_type=product_type
        )

        message = [{"role": "user", "content": prompt}]
        logging.info(f"Prompt: {prompt}")

        product_name = self.chat(message, 1.25, 80)
        logging.info(f"Generated product name: {product_name}")

        if not product_name:
            raise ValueError(f"Failed to generate product name with prompt: {prompt}")

        return product_name
        