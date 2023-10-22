import os
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
    message = gm.generate_message(entity, product, sentiment, message_type)

    embedding_response = openai.Embedding.create(
        input=message,
        model='text-embedding-ada-002'
    )

    embedding = embedding_response['data'][0]['embedding']

    data = {
        'event_type': event_type,
        'event_details': message,
        'embedding': embedding
    }
    
    data = supabase.table('events').insert(data).execute()

def agent_test():
    agent = Agent(api_key, supabase, 0)
    agent.observe()

if __name__ == '__main__':
    # game_master_test()
    agent_test()


