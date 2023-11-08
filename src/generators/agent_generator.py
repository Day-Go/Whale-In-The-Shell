import logging

from generators.entity_generator import EntityGenerator
from llm import LLM
from data_access_object import DataAccessObject


class AgentGenerator(LLM, EntityGenerator):
    def __init__(self, api_key: str, dao: DataAccessObject):
        LLM.__init__(self, api_key)
        EntityGenerator.__init__(self)
        self.dao = dao

        self.system_prompt = self.dao.get_prompt_by_name('AG_SystemPrompt')

    def create(self):

        try:
            nationality = self.dao.get_nationality_by_id(23)
            occupation = self.dao.get_occupation_by_id(78)

            agent_name = self.generate_agent_attribute(
                'AG_GenAgentName', nationality=nationality, occupation=occupation
            )
            agent_handle = self.generate_agent_attribute(
                'AG_GenAgentHandle', nationality=nationality, 
                occupation=occupation, agent_name=agent_name
            )
            agent_bio = self.generate_agent_attribute(
                'AG_GenAgentBio', nationality=nationality, 
                occupation=occupation, agent_name=agent_name
            )

            response = self.dao.insert(
                'agents',
                name=agent_name,
                handle=agent_handle,
                occupation=occupation,
                nationality=nationality,
                biography=agent_bio
            )

            return response.data[0]
        
        except Exception as e:
            # Properly handle exceptions and log the error
            logging.error(f'Failed to create new agent: {e}')
            raise


        # Generate name

        # Create biography

        # Insert into database
        pass

    def update(self, agent):
        # Logic to update an agent
        pass

    def deactivate(self, agent):
        # Logic to deactivate an agent
        pass

    def generate_agent_attribute(self, prompt_name: str, **kwargs) -> str:
        prompt = self.dao.get_prompt_by_name(prompt_name).format(**kwargs)
        message = [{'role': 'system', 'content': self.system_prompt}, 
                   {'role': 'user', 'content': prompt}]
        logging.info(f'Prompt: {prompt}')

        agent_attribute = self.chat(message, 1.25, 80)
        logging.info(f'Generated attribute: {agent_attribute}')

        if not agent_attribute:
            raise ValueError(f'Failed to generate agent attribute with prompt: {prompt}')

        return agent_attribute