import os
import traceback
from abc import ABC, abstractmethod
from getpass import getpass

import requests
from langchain import LLMChain, PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.llms import Banana, CerebriumAI

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
            "Authorization": f"Bearer {os.environ.get('RUNPOD_API_KEY')} ",
        }

    def get_response(self, option: any):
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
            raise Exception(traceback.format_exc())


"""
class CerebriumService(BaseService):
    def __init__(self):
        from cerebrium import Conduit, model_type

        self.api_key = os.environ["CEREBRIUM_API_KEY"]
        self.c = Conduit(
            'hf-gpt',
            self.api_key,
            [
                (model_type.HUGGINGFACE_PIPELINE, {"task": "text-generation", "model": "EleutherAI/gpt-neo-125M", "max_new_tokens": 100}),
            ],
        )

        self.c.deploy()
        # Assume the endpoint is stored in self.c.endpoint after calling c.deploy()
        self.endpoint = self.c.endpoint

    def get_response(self, message: str, option: any):
        headers = {
            "Authorization": self.api_key,
            "Content-Type": "application/json"
        }
        response = requests.post(
            self.endpoint, headers=headers, json=[message]
        )
        if response.status_code == 200:
            return response.json()[0]["generated_text"]
        else:
            raise Exception("Failed to get response")
 """


class HuggingFaceService(BaseService):
    def __init__(self):
        self.endpoint = (
            "https://ramrhljba6iem7y4.us-east-1.aws.endpoints.huggingface.cloud"
        )
        self.headers = {
            "Authorization": f"Bearer {os.environ.get('HUGGINGFACE_API_KEY')}",
            "Content-Type": "text/plain",
        }

    def get_response(self, message: str, option: any = None):
        response = requests.post(self.endpoint, headers=self.headers, data=message)
        if response.status_code == 200:
            return response.json()["generated_text"]
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


class TextGenService(BaseService):
    def __init__(self):
        self.HOST = "qw8gpt1wsydz97-5000.proxy.runpod.net"
        self.URI = f"https://{self.HOST}/api/v1/chat"

    def get_response(self, user_input: str, history: list, username: str):
        history = {"internal": [history], "visible": [history]}
        request = {
            "user_input": user_input,
            "max_new_tokens": 200,
            "history": history,
            "mode": "chat-instruct",  # Valid options: 'chat', 'chat-instruct', 'instruct'
            "character": "Estefania, the horniest Latina on OF",
            "instruction_template": "Vicuna-v1.1",
            "your_name": username,
            "regenerate": False,
            "_continue": False,
            "stop_at_newline": False,
            "chat_generation_attempts": 1,
            "chat-instruct_command": 'Continue the chat dialogue below. Write a single reply for the character "<|character|>".\n\n<|prompt|>',
            "preset": "simple-1",
            "do_sample": True,
            "temperature": 0.5,
            "top_p": 0.9,
            "typical_p": 1,
            "epsilon_cutoff": 0,  # In units of 1e-4
            "eta_cutoff": 0,  # In units of 1e-4
            "tfs": 1,
            "top_a": 0,
            "repetition_penalty": 1.15,
            "repetition_penalty_range": 0,
            "top_k": 20,
            "min_length": 0,
            "no_repeat_ngram_size": 0,
            "num_beams": 1,
            "penalty_alpha": 0,
            "length_penalty": 1,
            "early_stopping": False,
            "mirostat_mode": 0,
            "mirostat_tau": 5,
            "mirostat_eta": 0.1,
            "seed": -1,
            "add_bos_token": True,
            "truncation_length": 2048,
            "ban_eos_token": False,
            "skip_special_tokens": True,
            "stopping_strings": [],
        }

        response = requests.post(self.URI, json=request)
        if response.status_code == 200:
            result = response.json()["results"][0]["history"]
            return result["visible"][-1][1]
        else:
            raise Exception(f"Failed to get response : {traceback.format_exc()}")


class Service:
    def __init__(self, service: BaseService):
        self.service = service

    def get_response(self, message: str, option: any):
        return self.service.get_response(message, option)


# Instances of our deployed LLM models
openai_service = OpenAIService()
banana_service = BananaService()
replica_service = ReplicaService()
http_service = HttpService("http://195.60.167.43:10458/api/v1/predict")
textgen_service = TextGenService()

# huggingface_service = HuggingFaceService()
# cerebrium_service = CerebriumService()
