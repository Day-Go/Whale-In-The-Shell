import os
import json
import openai
import logging
from qdrant_client import QdrantClient
from game_master import GameMaster
from supabase import create_client, Client

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

key = os.getenv('OPENAI_API')
openai.api_key = key

if __name__ == "__main__":
    api_key = os.getenv('OPENAI_API')
    openai.api_key = api_key

    gm = GameMaster(api_key, supabase)

    gm.set_system_prompt()
    gm.generate_announcement("Big Boys", "Big Coin", "neutral")


