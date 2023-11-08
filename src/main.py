import os
import re
import ast
import vecs
import openai
import numpy as np
from supabase import create_client, Client

from agent import Agent
from game_master import GameMaster
from generators import OrgGenerator, AgentGenerator
from data_access_object import DataAccessObject
from models.enums import Event 

url: str = os.getenv('SUPABASE_URL')
key: str = os.getenv('SUPABASE_SERVICE_KEY')

supabase: Client = create_client(url, key)

dao = DataAccessObject(supabase)
api_key = os.getenv('OPENAI_API')
openai.api_key = api_key


def agent_test():
    agent_id = 2
    agent = Agent(api_key, supabase, agent_id)
    response = agent.observe()

def embedding_similarity_test(query_embedding):
    response = supabase.table('memories').select('id, embedding').execute()
    # print(response.data[1])

    for row in response.data[:-1]:
        memory_id = row['id']
        embedding = ast.literal_eval(row['embedding'])
        similarity = np.dot(np.array(query_embedding), np.array(embedding))

        print(similarity)

def new_org_test():
    org_generator = OrgGenerator(api_key, dao)
    agent_generator = AgentGenerator(api_key, dao)
    gm = GameMaster(api_key, dao, org_generator, agent_generator)
    gm.timestep()

if __name__ == '__main__':
    new_org_test()
    # agent_test()
    # embedding_similarity_test([None])


