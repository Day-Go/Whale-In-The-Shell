import re
import openai
import logging
from supabase import Client

from llm import LLM
from data_access_object import DataAccessObject


class Agent(LLM):
    def __init__(self, agent_id: int, api_key: str, dao: DataAccessObject):
        super().__init__(api_key)
        self.id = agent_id
        self.dao = dao

        self.get_agent_information()
        self.system_prompt = self.get_system_prompt()

    def get_agent_information(self) -> None:
        response = self.dao.get_agent_by_id(self.id)
        self.__dict__.update(response)
        
    def get_system_prompt(self) -> None:
        prompt = self.dao.get_prompt_by_name('A_SystemPrompt')

        system_prompt = prompt.format(
            agent_name=self.name, agent_bio=self.biography,
            investment_style=self.investment_style, risk_tolerance=self.risk_tolerance,
            communication_style=self.communication_style)

        return system_prompt

    def form_opinion(self, subject):
        prompt = self.dao.get_prompt_by_name('A_SubjectOpinion')
        prompt = prompt.format(subject=subject)

        message = [{'role' :'system', 'content': self.system_prompt},
                     {"role": "user", "content": prompt}]
        
        opinion = self.chat(message, 1.25, 80)
        logging.info(f'Opinion: {opinion}')

        return opinion

    def update_goal(self, opinion: str):
        prompt = self.dao.get_prompt_by_name('A_UpdateGoal')
        prompt = prompt.format(opinion=opinion)
        logging.info(f'Prompt: {prompt}')

        message = [{'role' :'system', 'content': self.system_prompt},
                   {"role": "user", "content": prompt}]

        goal = self.chat(message, 1.25, 150)
        logging.info(f'Goal: {goal}')

        self.dao.update('agents', self.id, goals=goal)

    def observe(self, event_id: int):
        event = self.dao.get_event_by_id(event_id)
        product = self.dao.get_product_by_event_id(event_id)

        subject_opinion = self.form_opinion(product['type'])
        logging.info(f'Subject opinion: {subject_opinion}')

        prompt = self.dao.get_prompt_by_name('A_EventOpinion')
        prompt = prompt.format(
            event=event['event_details'], product_type=product['type'],
            opinion=subject_opinion, product_name=product['name'])
        logging.info(f'Prompt: {prompt}')

        message = [{'role' :'system', 'content': self.system_prompt},
                   {"role": "user", "content": prompt}]
        
        product_opinion = self.chat(message, 1.25, 80)
        logging.info(f'Product opinion: {product_opinion}')

        opinion_fragments = product_opinion.split('.')[:-1]
        for fragment in opinion_fragments:
            self.dao.insert(
                'agentsopinions', agent_id=self.id, 
                subject=product['type'], opinion=fragment,
                embedding=self.generate_embedding(fragment)
            )
            
        
    def reflect(self):
        pass

    def plan(self):
        pass

    def insert_memory(self, response: str, event_id: int):
        pass

