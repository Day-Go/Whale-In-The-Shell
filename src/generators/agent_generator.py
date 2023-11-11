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
            nationality = self.dao.get_random_nationality()
            occupation = self.dao.get_random_occupation()
            traits = self.dao.get_n_random_traits(5)
            investment_style = self.dao.get_random_investment_style()
            risk_tolerance = self.dao.get_random_risk_tolerance()
            communication_style = self.dao.get_random_communication_style()

            agent_name = self.generate_agent_attribute(
                'AG_GenAgentName', tok_limit=10, temp=1.25,
                 nationality=nationality, occupation=occupation
            )
            agent_handle = self.generate_agent_attribute(
                'AG_GenAgentHandle', tok_limit=10, temp=1.5, 
                traits=traits, communication_style=communication_style
            )
            agent_bio = self.generate_agent_attribute(
                'AG_GenAgentBio', tok_limit=150, temp=1.25 ,
                nationality=nationality, occupation=occupation, 
                agent_name=agent_name, traits=traits
            )

            response = self.dao.insert(
                'agents',
                name=agent_name, handle=agent_handle, occupation=occupation,
                nationality=nationality, biography=agent_bio, 
                investment_style=investment_style, risk_tolerance=risk_tolerance,
                communication_style=communication_style
            )

            for trait in traits:
                self.dao.insert(
                    'agentstraits',
                    agent_id=response.data[0]['id'],
                    trait_id=trait['id'],
                    is_positive=trait['is_positive']
                )

            return response.data[0]
        
        except Exception as e:
            # Properly handle exceptions and log the error
            logging.error(f'Failed to create new agent: {e}')
            raise

        pass

    def update(self, agent):
        # Logic to update an agent
        pass

    def deactivate(self, agent):
        # Logic to deactivate an agent
        pass

    def generate_agent_attribute(self, prompt_name: str, tok_limit: int, 
                                 temp: float, **kwargs) -> str:
        if 'traits' in kwargs:
            traits_list = kwargs['traits']
            # Convert the list of trait dictionaries into a string representation
            traits_str = ', '.join([f"{trait['trait']}" 
                                    for trait in traits_list])

            kwargs['traits'] = traits_str

        prompt = self.dao.get_prompt_by_name(prompt_name).format(**kwargs)
        if prompt_name == 'AG_GenAgentBio':
            message = [{'role': 'system', 'content': self.system_prompt}, 
                       {'role': 'user', 'content': prompt}]
        else:
            message = [{'role': 'user', 'content': prompt}]

        logging.info(f'Prompt: {prompt}')

        agent_attribute = self.chat(message, temp=temp, max_tokens=tok_limit)
        logging.info(f'Generated attribute: {agent_attribute}')

        if not agent_attribute:
            raise ValueError(f'Failed to generate agent attribute with prompt: {prompt}')

        return agent_attribute
    