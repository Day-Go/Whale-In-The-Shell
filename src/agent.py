import json
import random
import logging
import asyncio
from openai import OpenAI, AsyncOpenAI

from llm import LLM
from data_access_object import DataAccessObject
from observer import ObserverManager

class Agent(LLM):
    def __init__(
            self, 
            agent_id: int, 
            gpt_client: OpenAI,
            async_gpt_client: AsyncOpenAI,
            dao: DataAccessObject) -> None:
        super().__init__(gpt_client, async_gpt_client)
        self.id = agent_id
        self.dao = dao
        self.wallet = {}

        self.load_agent_parameters()
        self.load_agent_wallet()
        self.system_prompt = self.get_system_prompt()


    '''
    Initialisation methods
    ''' 
    def load_agent_parameters(self) -> None:
        '''
        Get agent traits from database and load them into the instance dict
        '''
        response = self.dao.get_agent_by_id(self.id)
        self.__dict__.update(response)
        
    def load_agent_wallet(self) -> None:
        '''
        Get agent wallet from database and load them into self.wallet
        '''
        self.wallet.update({'USD': self.balance})
        wallet = self.dao.get_agent_wallet_by_id(self.id)

        for asset in wallet:
            asset_ticker = self.dao.get_asset_by_id(asset['asset_id'])['ticker']
            self.wallet[asset_ticker] = asset['balance']

    def format_wallet(self):
        '''
        Convert items in self.wallet to a string for use in prompts

        Returns:
            formatted_string (str): A formatted string of the agent's wallet
        '''
        formatted_entries = [f"{balance} {currency}" for currency, balance in self.wallet.items()]
        formatted_string = ', '.join(formatted_entries)

        return formatted_string

    def get_system_prompt(self) -> None:
        '''
        Get the system prompt for the agent from the database and format it 
        with the agents traits

        Returns:
            system_prompt (str): The formatted system prompt
        '''
        prompt = self.dao.get_prompt_by_name('A_SystemPrompt')
        agent_balance = self.format_wallet()

        system_prompt = prompt.format(
            agent_name=self.name, agent_bio=self.biography, agent_balance=agent_balance,
            investment_style=self.investment_style, risk_tolerance=self.risk_tolerance,
            communication_style=self.communication_style
        )
        logging.info(f'System prompt: {system_prompt}')

        return system_prompt

    def get_agent_traits_prompt(self) -> None:
        '''
        Get the agent traits prompt from the database and format it with the
        agent's traits. This is similar to the system prompt but doesn't
        include the agents biography

        Returns:
            agent_traits_prompt (str): The formatted agent traits prompt
        '''
        agent_traits_prompt = self.dao.get_prompt_by_name('A_AgentTraits')
        agent_traits_prompt = agent_traits_prompt.format(
            agent_name=self.name, agent_balance=self.format_wallet(),
            investment_style=self.investment_style, risk_tolerance=self.risk_tolerance,
            communication_style=self.communication_style
        )

        return agent_traits_prompt

    '''
    Agent actions
    Methods for when the agent needs to interact with external world state.
    These methods should be called from the agent's cognitive functions.
    '''
    async def observe(self, event_id: int):
        # Get event and product information
        event = self.dao.get_event_by_id(event_id)
        product = self.dao.get_product_by_event_id(event_id)

        # Form an opinion on the product type, if the opinion doesnt
        # already exist in the database
        subject_opinion = await self.form_opinion(product['type'])
        logging.info(f'Subject opinion: {subject_opinion}')

        # Form an opinion on the specific product
        prompt = self.dao.get_prompt_by_name('A_EventOpinion')
        prompt = prompt.format(
            event=event['event_details'], product_type=product['type'],
            opinion=subject_opinion, product_name=product['name'])
        logging.info(f'Prompt: {prompt}')

        message = [{'role' :'system', 'content': self.system_prompt},
                   {"role": "user", "content": prompt}]
        
        product_opinion = await self.chat_async(message, 1.25, 80)
        logging.info(f'Product opinion: {product_opinion}')

        opinion_fragments = product_opinion.split('.')[:-1]
        for fragment in opinion_fragments:
            self.dao.insert(
                'agentsopinions', agent_id=self.id, 
                subject=product['type'], opinion=fragment,
                embedding=self.generate_embedding(fragment)
            )

        await self.decide(product['name'], product_opinion)

    def buy(self, asset_name: str, allocation: float, reason: str):
        '''
        For when the agent has decided to buy an asset. Update the agent's
        wallet and the asset's market cap in the database.

        Args:
            asset_name (str): The name of the asset to buy
            allocation (float): The percentage of the agent's wallet to allocate
            reason (str): The reason for buying the asset
        '''

        logging.info(f'Buying {allocation}% of {asset}...')
        logging.info(f'Reason: {reason}')
        buy_amount = self.wallet['USD'] * (allocation / 100)
        self.wallet['USD'] -= buy_amount

        print(self.wallet)
        logging.info(self.wallet)
        asset = self.dao.get_asset_by_name(asset_name)
        asset['market_cap'] += buy_amount
        ticker = asset['ticker']
        if ticker in self.wallet:
            self.wallet[ticker] += buy_amount * asset['price']
        else:
            self.wallet[ticker] = buy_amount * asset['price']

        for key, val in self.wallet.items():
            wallet_table_id = self.dao.get_wallet_row_by_agentasset_id(self.id, asset['id'])
            self.dao.update('wallet', wallet_table_id, balance=val)

        self.dao.update('agents', self.id, balance=self.wallet['USD'])
        self.dao.update('asset', asset['id'], market_cap=asset['market_cap'])

    def sell(self, asset: str, allocation: float, reason: str):
        '''
        Similar to buy but for when the agent decides to sell.

        Args:
            asset (str): The name of the asset to sell
            allocation (float): The percentage of the agent's asset holdings to sell
            reason (str): The reason for selling the asset
        '''

        logging.info(f'Selling {allocation}% of {asset}...')
        logging.info(f'Reason: {reason}')
        if self.wallet[asset] < allocation:
            logging.info(f'Insufficient {asset} to sell.')
            return
        
        sell_amount = self.wallet[asset] * (allocation / 100)
        self.wallet[asset] -= sell_amount
        self.wallet['USD'] += sell_amount * asset['price']

        self.dao.update('agents', self.id, balance=self.wallet['USD'])

        asset = self.dao.get_asset_by_name(asset)
        asset['market_cap'] -= sell_amount

        for key, val in self.wallet.items():
            wallet_table_id = self.dao.get_wallet_row_by_agentasset_id(self.id, asset['id'])
            self.dao.update('wallet', wallet_table_id, balance=val)

        self.dao.update('asset', asset['id'], market_cap=asset['market_cap'])

    def abstain(self, reason: str):
        '''
        Placeholder for when the agent decides to abstain from buying or selling.
        Used to give the agent a choice when function calling.
        '''
        logging.info(f'Abstaining... {reason}')

    def post(self, content: str):
        pass

    def comment(self, content: str):
        pass

    def reply(self, content: str):
        pass

    def upvote(self, content: str):
        pass

    def share(self, content: str):
        pass

    '''
    Main loop
    '''
    async def run(self):
        '''
        Continuous loop for the agent to run in.
        '''
        logging.info(f'Agent {self.id} running...')
        while True:
            await self.sleep()

            # Focus on the observation
            # 1. How do we select an event? 
            # Timestamp and embedding. 
            event = self.dao.get_random_event()
            await self.update(event)

    async def update(self, event):
        print(f'Agent {self.id} Updating...\n\n')
        # Decide whether to observe the event
        # For now use a simple probability
        if random.random() < 1:
            await self.observe(event['id'])

    '''
    Cognitive functions
    '''
    async def form_opinion(self, subject: str):
        prompt = self.dao.get_prompt_by_name('A_SubjectOpinion')
        prompt = prompt.format(subject=subject)

        message = [{'role' :'system', 'content': self.system_prompt},
                     {"role": "user", "content": prompt}]
        
        opinion = await self.chat_async(message, 1.25, 80)
        logging.info(f'Opinion: {opinion}')

        return opinion

    # product name should be replaced with something more generic.
    # In the future agents may decide on more than just products.
    async def decide(self, product_name: str, opinion: str):
        agent_traits_prompt = self.get_agent_traits_prompt()

        options = ', '.join(['buy', 'sell', 'abstain'])
        prompt = self.dao.get_prompt_by_name('A_Decide')
        prompt = prompt.format(product_name=product_name, opinion=opinion, options=options)
        logging.info(f'Prompt: {prompt}')

        entire_prompt = f'{agent_traits_prompt}\n{prompt}'

        message = [{"role": "user", "content": entire_prompt}]
        
        response = await self.function_call_async(
            message, 
            functions=self.get_buy_sell_functions()
        )
        logging.info(response)

        if response == None:
            logging.info('No response from agent.')
            return

        function_name = response.name
        function_args = json.loads(response.arguments)

        eval(f'self.{function_name}(**function_args)')

    def update_goal(self, opinion: str):
        prompt = self.dao.get_prompt_by_name('A_UpdateGoal')
        prompt = prompt.format(opinion=opinion)
        logging.info(f'Prompt: {prompt}')

        message = [{'role' :'system', 'content': self.system_prompt},
                   {"role": "user", "content": prompt}]

        goal = self.chat(message, 1.25, 150)
        logging.info(f'Goal: {goal}')

        self.dao.update('agents', self.id, goals=goal)

    def reflect(self):
        pass

    def plan(self):
        pass

    def insert_memory(self, response: str, event_id: int):
        pass

    '''
    Utility functions
    '''
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
                            "type": "integer",
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
                            "type": "integer",
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

    def get_sleep_duration(self):
        attentiveness = random.randint(1, 10)
        min_delay = attentiveness * 2
        max_delay = attentiveness * 5
        sleep_duration = random.randint(min_delay, max_delay)

        return sleep_duration

    async def sleep(self):
        sleep_duration = self.get_sleep_duration()
        await asyncio.sleep(1)

    