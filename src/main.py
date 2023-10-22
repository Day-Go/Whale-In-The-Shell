import os
import openai
from game_master import GameMaster
from supabase import create_client, Client

url: str = os.getenv('SUPABASE_URL')
key: str = os.getenv('SUPABASE_KEY')
supabase: Client = create_client(url, key)

key = os.getenv('OPENAI_API')
openai.api_key = key

if __name__ == '__main__':
    api_key = os.getenv('OPENAI_API')
    openai.api_key = api_key

    gm = GameMaster(api_key, supabase)

    gm.set_system_prompt()

    entity = 'Big Boys'
    product = 'Big Coin'
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
