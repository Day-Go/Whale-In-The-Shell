import re
import openai
import logging
from supabase import Client

from llm import LLM
from data_access_object import DataAccessObject

logging.basicConfig(level=logging.INFO)

class Agent(LLM):
    def __init__(self, agent_id: int, api_key: str, dao: DataAccessObject):
        super().__init__(api_key)
        self.id = agent_id
        self.dao = dao

        self.get_agent_information()

    def get_agent_information(self) -> None:
        response = self.dao.get_agent_by_id(self.id)
        self.__dict__.update(response)
        
    def get_system_prompt(self) -> None:
        prompt = self.dao.get_prompt_by_name('A_SystemPrompt')

        system_prompt = prompt.format(
            agent_name=self.name, agent_bio=self.biography,
            investment_style=self.investment_style, risk_tolerance=self.risk_tolerance,
            communication_style=self.communication_style)
        
        logging.info(f'System prompt: {system_prompt}')
        return system_prompt

    def form_opinion(self):
        pass

    def update_goal(self):
        system_prompt = self.get_system_prompt()

        prompt = self.dao.get_prompt_by_name('A_UpdateGoal')
        logging.info(f'Prompt: {prompt}')

        message = [{'role' :'system', 'content': system_prompt},
                   {"role": "user", "content": prompt}]

        goal = self.chat(message, 1.25, 80)
        logging.info(f'Goal: {goal}')

        self.dao.update('agents', self.id, goals=goal)

    def observe(self):
        pass

    def reflect(self):
        pass

    def plan(self):
        pass

    def insert_memory(self, response: str, event_id: int):
        pass