import logging

from generators.entity_generator import EntityGenerator
from llm import LLM
from data_access_object import DataAccessObject

class OrgGenerator(LLM, EntityGenerator):
    def __init__(self, api_key: str, dao: DataAccessObject):
        LLM.__init__(self, api_key)
        EntityGenerator.__init__(self)
        self.dao = dao

    def create(self):
        try:
            org_type = self.dao.get_org_type_by_id(2)
            org_name = self.generate_org_attribute(
                'OG_GenOrgName', org_type=org_type
            )
            org_mission = self.generate_org_attribute(
                'OG_GenOrgMission', org_type=org_type, org_name=org_name
            )
            org_desc = self.generate_org_attribute(
                'OG_GenOrgDesc', org_type=org_type, 
                org_name=org_name, org_mission=org_mission
            )

            response = self.dao.insert(
                'organisations',
                name=org_name,
                type=org_type,
                description=org_desc,
                mission=org_mission
            )

            return response.data[0]
        except Exception as e:
            # Properly handle exceptions and log the error
            logging.error(f"Failed to create new organisation: {e}")
            raise

    def update(self, organization):
        # Logic to update an organization
        pass

    def deactivate(self, organization):
        # Logic to deactivate an organization
        pass

    def generate_org_attribute(self, prompt_name: str, **kwargs) -> str:
        prompt = self.dao.get_prompt_by_name(prompt_name).format(**kwargs)
        message = [{"role": "user", "content": prompt}]
        logging.info(f"Prompt: {prompt}")

        org_attribute = self.chat(message, 1.25, 80)
        logging.info(f"Generated attribute: {org_attribute}")

        if not org_attribute:
            raise ValueError(f"Failed to generate organisation attribute with prompt: {prompt}")

        return org_attribute

    def create_new_product(self, **kwargs) -> str:
        product_type = self.dao.get_random_crypto_product()
        product_name = self.generate_product_name(
            org_type=kwargs.get('org_type'), 
            org_name=kwargs.get('org_name'), 
            product_type=product_type
        )

        response = self.dao.insert(
            'products',
            org_id=kwargs.get('org_id'), 
            name=product_name
        )

        return response.data[0]

    def generate_product_name(self, **kwargs) -> str:
        org_type = kwargs.get('org_type')
        org_name = kwargs.get('org_name')
        product_type = kwargs.get('product_type')

        prompt = self.dao.get_prompt_by_name('OG_GenProductName').format(
            org_type=org_type, org_name=org_name, product_type=product_type
        )

        message = [{"role": "user", "content": prompt}]
        logging.info(f"Prompt: {prompt}")

        product_name = self.chat(message, 1.25, 80)
        logging.info(f"Generated product name: {product_name}")

        if not product_name:
            raise ValueError(f"Failed to generate product name with prompt: {prompt}")

        return product_name
        