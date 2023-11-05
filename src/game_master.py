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
        new_entity = self.create_new_entity()
        logging.info(f"Created new entity with id {new_entity['id']}")

        new_product = self.create_new_product(
            entity_id=new_entity['id'], 
            entity_type=new_entity['type'], 
            entity_name=new_entity['name']
        )
        logging.info(f"Created new product with id {new_product['id']}")

        system_prompt =  self.dao.get_prompt_by_name('GM_SystemPrompt')
        prompt = self.dao.get_prompt_by_name('GM_Announcement')
        prompt = prompt.format(
            event='launch announcement', 
            product=new_product['name'], 
            entity=new_entity['name']
        )
        logging.info(f"Prompt: {prompt}")

        message = [
            {"role": "system", "content": system_prompt}, 
            {"role": "user", "content": prompt}
        ]

        event = self.chat(message, temp=1.2, max_tokens=80)
        event_embedding = self.generate_embedding(event)
        logging.info(f"Generated announcement: {event}")

        event_row = self.dao.insert(
            'events',
            event_type=Event.ANNOUNCEMENT.value, 
            event_details=event, 
            embedding=event_embedding
        )

        event_entities_row = self.dao.insert(
            'eventsentities',
            event_id=event_row.data[0]['id'],
            entity_id=new_entity['id']
        )

        event_products_row = self.dao.insert(
            'eventsproducts',
            event_id=event_row.data[0]['id'],
            product_id=new_product['id']
        )

    def generate_development():
        pass

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
            product_name=product_name
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
        