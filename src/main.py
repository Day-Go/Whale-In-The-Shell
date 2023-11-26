import os
import random
import datetime
import logging
from supabase import create_client, Client
from openai import OpenAI

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
observer_manager = ObserverManager()


if __name__ == '__main__':
    gm = GameMaster(
        api_key, 
        dao, 
        OrgGenerator(gpt_client, dao), 
        AgentGenerator(gpt_client, dao),
        observer_manager
    )

    ag = AgentGenerator(gpt_client, dao)
    org = OrgGenerator(gpt_client, dao)

    while True:
        while random.random() < 0.5:
            ag.create()

        while random.random() < 0.25:
            org.create()

        gm.timestep()
        input('Press enter to continue...')



