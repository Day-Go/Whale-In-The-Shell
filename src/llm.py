import openai
import logging

class LLM:
    def __init__(self, api_key: str):
        openai.api_key = api_key
        
    def generate_embedding(self, message):
        response_embedding = openai.Embedding.create(
            input=message,
            model='text-embedding-ada-002'
        )
        embedding = response_embedding['data'][0]['embedding']
        return embedding

    def chat(self, message):
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=message,
            temperature=1.2,
            max_tokens=80
        )

        reply_content = completion.choices[0].message['content'] 
        return reply_content