import os
from pathlib import Path

import pandas as pd
import pinecone
from dotenv import load_dotenv
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Pinecone

from products.products import ProductService

# Loading OPENAI, PINECONE API KEYS
env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")


class PineconeService(ProductService):
    def __init__(self) -> None:
        self.initialized = False
        pass

    def initialize(self):
        if self.initialized == True:
            return

        try: 
            # Pinecone initialize index
            pinecone.init(api_key=PINECONE_API_KEY, environment="us-east1-gcp")

            dimension = 1536
            index_name = "import-product"
            if index_name not in pinecone.list_indexes():
                print("Index is not existed")
                return

            # Get the vectorstore and add new products
            self.index = pinecone.Index(index_name)
            self.openai = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
            self.vectorstore = Pinecone(self.index, self.openai.embed_query, "text")
            
        except Exception as e:
            print (f"Exception in PineconeService: {str(e)}")

        self.initialized = True
        pass

    def match_product(self, messages: str):
        self.initialize()
        if self.vectorstore is None:
            return "Error happened to connect pinecone"

        docs = self.vectorstore.similarity_search(messages, k=1)
        return docs[0].page_content

    def get_bestseller_products(self):
        pass

    def get_product_list(self):
        pass
