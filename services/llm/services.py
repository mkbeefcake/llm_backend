import os
from abc import ABC, abstractmethod
from getpass import getpass
import requests


from langchain.llms import Banana
from langchain.chat_models import ChatOpenAI
from langchain import PromptTemplate, LLMChain

# Define a base class for all services
class BaseService(ABC):
    @abstractmethod
    def get_response(self, message: str, option: str):
        pass


class OpenAIService(BaseService):
    def __init__(self):
        #os.environ["OPENAI_API_KEY"]
        template = """Question: {question}
        Answer: Let's think step by step."""
        self.prompt = PromptTemplate(template=template, input_variables=["question"])
        self.llm = ChatOpenAI()
        self.llm_chain = LLMChain(prompt=self.prompt, llm=self.llm)

    def get_response(self, message: str, option: str):
        return self.llm_chain.run(message)


class BananaService(BaseService):
    def __init__(self):
        #os.environ["BANANA_API_KEY"]
        template = """Question: {question}
        Answer: Let's think step by step."""
        self.prompt = PromptTemplate(template=template, input_variables=["question"])
        self.llm = Banana(model_key=os.environ["BANANA_MODEL_KEY"])
        self.llm_chain = LLMChain(prompt=self.prompt, llm=self.llm)

    def get_response(self, message: str, option: str):
        return self.llm_chain.run(message)

class HttpService(BaseService):
    def __init__(self, endpoint: str):
        self.endpoint = endpoint

    def get_response(self, message: str, option: str):
        headers = {"Content-Type": "application/json"}
        response = requests.post(
            self.endpoint, headers=headers, json={"input_text": message}
        )
        if response.status_code == 200:
            return {"message": response.json()["result"]}
        else:
            return {"message": "Failed to get response"}

class Service:
    def __init__(self, service: BaseService):
        self.service = service

    def get_response(self, message: str, option: str):
        return self.service.get_response(message, option)


# Create instances of OpenAI and Banana services
openai_service = Service(OpenAIService())
banana_service = Service(BananaService())
http_service = Service(HttpService("http://195.60.167.43:10458/api/v1/predict"))
