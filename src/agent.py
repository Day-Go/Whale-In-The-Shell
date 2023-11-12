import json
import logging
from supabase import Client
from openai import OpenAI

from llm import LLM
from data_access_object import DataAccessObject


class Agent(LLM):
    def __init__(self, agent_id: int, gpt_client: OpenAI, dao: DataAccessObject):
        super().__init__(gpt_client)
        self.id = agent_id
        self.dao = dao
        self.wallet = {}

        self.get_agent_information()
        self.get_agent_wallet()
        self.system_prompt = self.get_system_prompt()

    def get_agent_information(self) -> None:
        response = self.dao.get_agent_by_id(self.id)
        self.__dict__.update(response)
        
    def get_agent_wallet(self) -> None:
        wallet = self.dao.get_agent_wallet_by_id(self.id)

        for asset in wallet:
            currency_code = self.dao.get_currency_by_id(asset['currency_id'])['code']
            self.wallet[currency_code] = asset['balance']

    def format_wallet(self):
        formatted_entries = [f"{balance} {currency}" for currency, balance in self.wallet.items()]
        formatted_string = ', '.join(formatted_entries)

        return formatted_string

    def get_system_prompt(self) -> None:
        prompt = self.dao.get_prompt_by_name('A_SystemPrompt')
        
        agent_balance = self.format_wallet()

        system_prompt = prompt.format(
            agent_name=self.name, agent_bio=self.biography, agent_balance=agent_balance,
            investment_style=self.investment_style, risk_tolerance=self.risk_tolerance,
            communication_style=self.communication_style)
        logging.info(f'System prompt: {system_prompt}')

        return system_prompt

    def get_buy_sell_functions(self):
        functions = [
            {
                "name": "buy",
                "description": "Buy the given product",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "asset": {
                            "type": "string",
                            "description": "the asset to buy, e.g. BTC, ETH, etc.",
                        },
                        "allocation": {
                            "type": "string",
                            "description": "The percentage of your wallet to allocate to the asset",
                        },
                        "reason": {
                            "type": "string",
                            "description": "Your reason for buying the asset",
                        }
                    },
                    "required": ["asset", "allocation", "reason"]
                }
            },
            {
                "name": "abstain",
                "description": "Do nothing",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "reason": {
                            "type": "string",
                            "description": "Your reason for obstaining",
                        }
                    },
                    "required": ["asset"]
                }
            },
            {
                "name": "sell",
                "description": "sell the given asset",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "asset": {
                            "type": "string",
                            "description": "the asset to sell, e.g. BTC, ETH, etc.",
                        },
                        "allocation": {
                            "type": "string",
                            "description": "The percentage of your asset holdings to sell",
                        },
                        "reason": {
                            "type": "string",
                            "description": "Your reason for selling the asset",
                        }
                    },
                    "required": ["asset", "allocation", "reason"]
                }
            }
        ]

        return functions

    def timestep(self):
        pass

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

        self.decide(product_opinion)
    
    def decide(self, opinion: str):
        agent_traits_prompt = self.dao.get_prompt_by_name('A_AgentTraits')
        agent_traits_prompt = agent_traits_prompt.format(
            agent_name=self.name, agent_balance=self.format_wallet(),
            investment_style=self.investment_style, risk_tolerance=self.risk_tolerance,
            communication_style=self.communication_style
        )

        options = ', '.join(['buy', 'sell', 'abstain'])
        prompt = self.dao.get_prompt_by_name('A_Decide')
        prompt = prompt.format(product_name=" NebulaLendonomy", opinion=opinion, options=options)
        logging.info(f'Prompt: {prompt}')

        entire_prompt = f'{agent_traits_prompt}\n{prompt}'

        message = [{"role": "user", "content": entire_prompt}]
        
        response = self.function_call(message, functions=self.get_buy_sell_functions())
        logging.info(response)

        function_name = response.name
        function_args = json.loads(response.arguments)

        eval(f'self.{function_name}(**function_args)')


    def reflect(self):
        pass

    def plan(self):
        pass

    def insert_memory(self, response: str, event_id: int):
        pass

    def buy(self, asset: str, allocation: float):
        logging.info(f'Buying {allocation}% of {asset}...')

    def sell(self, asset: str, allocation: float):
        logging.info(f'Selling {allocation}% of {asset}...')