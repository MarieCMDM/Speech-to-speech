import time

from langchain_openai import ChatOpenAI
from langchain.callbacks.base import BaseCallbackHandler
from langchain_core.messages.ai import AIMessage


class StreamHandler(BaseCallbackHandler):
    def __init__(self, timer):
        self.timer = timer

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        print(token)

        if token:
            if not self.timer['stop']:
                self.timer['stop'] = time.perf_counter()

class LLM:
    def __init__(self, 
                assistant_name: str, 
                api_key: str, 
                base_url: str,
                model_name: str,
                prompt: str = None):
        if prompt == None:
            self.__system_prompt = self.__use_default_prompt(assistant_name)
        else:
            self.__system_prompt = prompt 

        self.__api_key = api_key  
        self.__base_url = base_url
        self.__model_name = model_name
    
    def call(self, user_prompt: str) -> str:
        timer = dict(start=None, stop=None)
        client = ChatOpenAI(
            api_key=self.__api_key,
            base_url=self.__base_url,
            model=self.__model_name,
            callbacks=[StreamHandler(timer)],
            streaming=True
        )

        response_text = client.invoke(
            input=[
                {"role": "system", "content": self.__system_prompt},
                {"role": "user", "content": user_prompt},
            ]
        )

        return response_text.content

    def __use_default_prompt(self, name: str) -> str:
        return f"""
            You are an Ai Assistant with name: {name}.
            Give very concise answers unless you are explicitly asked to be detailed.
            Create more conversational sentences without using numbers, symbols, abbreviations and lists.
            """