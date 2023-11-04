import re
import openai
import logging

class LLM:
    def __init__(self, api_key: str):
        openai.api_key = api_key

    @staticmethod    
    def truncate_unfinished_sentence(response: str) -> str:
        matches = re.findall(r'\s*[^.!?]*[.!?]', response)
        return ''.join(matches).strip()

    def generate_embedding(self, message):
        response_embedding = openai.Embedding.create(
            input=message,
            model='text-embedding-ada-002'
        )
        embedding = response_embedding['data'][0]['embedding']
        return embedding

    def chat(self, message: str, temp: float, max_tokens: int) -> str:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=message,
            temperature=temp,
            max_tokens=max_tokens
        )

        reply_content = completion.choices[0].message['content'] 

        if '.' in reply_content:
            reply_content = self.truncate_unfinished_sentence(reply_content)
            
        return reply_content