import os
import re
import ast
import vecs
import openai
import numpy as np
from supabase import create_client, Client

from agent import Agent
from game_master import GameMaster
from data_access_object import DataAccessObject
from models.enums import Event 

url: str = os.getenv('SUPABASE_URL')
key: str = os.getenv('SUPABASE_SERVICE_KEY')

supabase: Client = create_client(url, key)

dao = DataAccessObject(supabase)
api_key = os.getenv('OPENAI_API')
openai.api_key = api_key

def game_master_test():
    gm = GameMaster(api_key, supabase)

    gm.set_system_prompt()

    entity = 'Fal Hinney'
    product = 'Link Swap'
    sentiment = 'neutral'
    event_type = Event.ANNOUNCEMENT
    response = gm.generate_message(entity, product, sentiment, event_type)

    response_embedding = openai.Embedding.create(
        input=response,
        model='text-embedding-ada-002'
    )

    embedding = response_embedding['data'][0]['embedding']

    data = {
        'event_type': event_type,
        'event_details': response,
        'embedding': embedding
    }
    
    print(response)
    supabase.table('events').insert(data).execute()
    # supabase.table('events')

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

def new_entity_test():
    gm = GameMaster(api_key, dao)
    gm.timestep()

if __name__ == '__main__':
    new_entity_test()
    # game_master_test()
    # agent_test()
    # embedding_similarity_test([None])


