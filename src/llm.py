import re
from openai import OpenAI, AsyncOpenAI


class LLM:
    def __init__(self, gpt_client: OpenAI, async_gpt_client: AsyncOpenAI):
        self.gpt_client = gpt_client
        self.async_gpt_client = async_gpt_client

    @staticmethod    
    def truncate_unfinished_sentence(response: str) -> str:
        matches = re.findall(r'\s*[^.!?]*[.!?]', response)
        return ''.join(matches).strip()

    def generate_embedding(self, message):
        response_embedding = self.gpt_client.embeddings.create(
            input=message,
            model='text-embedding-ada-002'
        )
        embedding = response_embedding.data[0].embedding
        return embedding

    async def generate_embedding_async(self, message):
        response_embedding = await self.async_gpt_client.embeddings.create(
            input=message,
            model='text-embedding-ada-002'
        )
        embedding = response_embedding.data[0].embedding
        return embedding

    def chat(self, message: str, temp: float, max_tokens: int) -> str:
        completion = self.gpt_client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=message,
            temperature=temp,
            max_tokens=max_tokens
        )

        reply_content = completion.choices[0].message.content

        if '.' in reply_content and len(reply_content) > 30:
            reply_content = self.truncate_unfinished_sentence(reply_content)
            
        return reply_content
    
    async def chat_async(self, message: str, temp: float, max_tokens: int) -> str:
        completion = await self.async_gpt_client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=message,
            temperature=temp,
            max_tokens=max_tokens
        )

        reply_content = completion.choices[0].message.content

        if '.' in reply_content and len(reply_content) > 30:
            reply_content = self.truncate_unfinished_sentence(reply_content)
            
        return reply_content

    def function_call(self, message: str, functions: list):
        completion = self.gpt_client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=message,
            functions=functions,
            function_call="auto"
        )

        function_call = completion.choices[0].message.function_call

        return function_call
    
    async def function_call_async(self, message: str, functions: list):
        completion = await self.async_gpt_client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=message,
            functions=functions,
            function_call="auto"
        )

        function_call = completion.choices[0].message.function_call
        if function_call == None:
            return FunctionCall

        return function_call