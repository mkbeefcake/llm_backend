import os
from abc import ABC, abstractmethod
from getpass import getpass

import requests
from langchain import LLMChain, PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.llms import Banana

from products.base import ProductBaseService


# Define a base class for all services
class BaseService(ABC):
    @abstractmethod
    def get_response(self, message: str, option: str):
        pass


class OpenAIService(BaseService):
    def __init__(self):
        # os.environ["OPENAI_API_KEY"]
        template = """Question: {question}
        Answer: Let's think step by step."""
        self.prompt = PromptTemplate(template=template, input_variables=["question"])
        self.llm = ChatOpenAI()
        self.llm_chain = LLMChain(prompt=self.prompt, llm=self.llm)

    def get_response(self, message: str, option: any):
        return self.llm_chain.run(message)


class BananaService(BaseService):
    def __init__(self):
        # os.environ["BANANA_API_KEY"]
        try:
            template = """Question: {question}
            Answer: Let's think step by step."""
            self.prompt = PromptTemplate(
                template=template, input_variables=["question"]
            )
            self.llm = Banana(model_key=os.environ["BANANA_MODEL_KEY"])
            self.llm_chain = LLMChain(prompt=self.prompt, llm=self.llm)
        except:
            pass

    def get_response(self, message: str, option: any):
        return self.llm_chain.run(message)


class ReplicaService(BaseService, ProductBaseService):
    def __init__(self):
        self.endpoint = "https://api.runpod.ai/v2/jycsr5gdh2lmqm/runsync"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer 43G8Y6TUI5HBXEW4LFJRWOZE2R40GME2ZRIXR1H7",
        }

    def get_response(self, message: str, option: any):
        response = requests.post(self.endpoint, headers=self.headers, json=option)
        if response.status_code == 200:
            return response.json()["output"]
        else:
            raise Exception("Failed to get response")

    def suggest_product(self, messages: any, option: any = None):
        response = requests.post(self.endpoint, headers=self.headers, json=option)
        if response.status_code == 200:
            return response.json()["output"]
        else:
            raise Exception("Failed to get response")


class HttpService(BaseService):
    def __init__(self, endpoint: str):
        self.endpoint = endpoint

    def get_response(self, message: str, option: any):
        headers = {"Content-Type": "application/json"}
        response = requests.post(
            self.endpoint, headers=headers, json={"input_text": message}
        )
        if response.status_code == 200:
            return response.json()["result"]
        else:
            raise Exception("Failed to get response")


class Service:
    def __init__(self, service: BaseService):
        self.service = service

    def get_response(self, message: str, option: any):
        return self.service.get_response(message, option)


PRICING_ENDPOINT = ""

# Create instances of OpenAI and Banana services
openai_service = OpenAIService()
banana_service = BananaService()
http_service = HttpService("http://195.60.167.43:10458/api/v1/predict")
pricing_service = HttpService(PRICING_ENDPOINT)
replica_service = ReplicaService()
