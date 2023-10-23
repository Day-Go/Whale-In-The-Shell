import os
import re
import openai
from supabase import create_client, Client

from agent import Agent
from game_master import GameMaster

url: str = os.getenv('SUPABASE_URL')
key: str = os.getenv('SUPABASE_KEY')
supabase: Client = create_client(url, key)

api_key = os.getenv('OPENAI_API')
openai.api_key = api_key


def game_master_test():
    gm = GameMaster(api_key, supabase)

    gm.set_system_prompt()

    entity = 'Fal Hinney'
    product = 'Link Swap'
    sentiment = 'neutral'
    message_type = 'announcement'
    event_type = f'{sentiment} {message_type}'
    response = gm.generate_message(entity, product, sentiment, message_type)

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
    
    supabase.table('events').insert(data).execute()

def agent_test():
    agent_id = 4
    agent = Agent(api_key, supabase, agent_id)
    response = agent.observe()

    # Responses can be cut off mid sentence due to token limit.
    # Use a regular expression to match complete sentences
    matches = re.findall(r'\s*[^.!?]*[.!?]', response)
    complete_paragraph = ''.join(matches).strip()

    response_embedding = openai.Embedding.create(
        input=complete_paragraph,
        model='text-embedding-ada-002'
    )

    embedding = response_embedding['data'][0]['embedding']

    data = {
        'agent_id': agent_id,
        'memory_details': complete_paragraph,
        'embedding': embedding
    }

    supabase.table('memories').insert(data).execute()




if __name__ == '__main__':
    # game_master_test()
    agent_test()


