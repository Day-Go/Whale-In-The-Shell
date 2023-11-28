import os
import asyncio
import random
import datetime
import logging
from supabase import create_client, Client
from openai import OpenAI, AsyncOpenAI

from agent import Agent
from game_master import GameMaster
from generators import OrgGenerator, AgentGenerator
from data_access_object import DataAccessObject
from observer import ObserverManager

# Create 'logs' directory if it doesn't exist
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Get the current date and time for the filename
current_time = datetime.datetime.now()
filename = os.path.join(log_dir, current_time.strftime("log_%Y%m%d_%H%M%S.txt"))

# Configure logging
logging.basicConfig(filename=filename, level=logging.DEBUG, 
                    format='%(asctime)s %(levelname)s:%(message)s', 
                    filemode='w')

url: str = os.getenv('SUPABASE_URL')
key: str = os.getenv('SUPABASE_SERVICE_KEY')

supabase: Client = create_client(url, key)

dao = DataAccessObject(supabase)
api_key = os.getenv('OPENAI_API')

gpt_client = OpenAI(api_key=api_key)
async_gpt_client = AsyncOpenAI(api_key=api_key)
observer_manager = ObserverManager()

def load_agents() -> list:
    # agent_ids = [120, 105, 151]
    agent_ids = [105]

    agents = []
    for agent_id in agent_ids:
        agents.append(
            Agent(agent_id, gpt_client, async_gpt_client, dao, observer_manager)
        )

    return agents

async def game_loop():
    while True:
        # while random.random() < 0.25:
        #     org.create()

        # while random.random() < 0.5:
        #     agent_id = ag.create()
        #     agent = Agent(agent_id, gpt_client, async_gpt_client, dao, observer_manager)
        #     break

        await gm.timestep()
        input('Press enter to continue...')


if __name__ == '__main__':
    ag = AgentGenerator(gpt_client, async_gpt_client, dao)
    og = OrgGenerator(gpt_client, async_gpt_client, dao)
    gm = GameMaster(gpt_client, async_gpt_client, dao, og, ag, observer_manager)

    agents = load_agents()
    for agent in agents:
        asyncio.run(agent.run())
    # asyncio.run(game_loop())



