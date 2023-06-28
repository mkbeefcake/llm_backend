import os
import uuid
from pathlib import Path

import pandas as pd
import pinecone
from dotenv import load_dotenv
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Pinecone

from core.utils.log import BackLog
from products.base import ProductBaseService

# Loading OPENAI, PINECONE API KEYS
env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_PRODUCT_INDEX = os.getenv("PINECONE_PRODUCT_INDEX")


class PineconeService(ProductBaseService):
    def __init__(self) -> None:
        self.initialized = False
        pass

    def initialize(self):
        if self.initialized == True:
            return

        try:
            # Pinecone initialize index
            pinecone.init(
                api_key=PINECONE_API_KEY, environment="northamerica-northeast1-gcp"
            )

            # Get the vectorstore and add new products
            dimension = 1536
            self.index = pinecone.Index(PINECONE_PRODUCT_INDEX)
            self.openai = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
            self.vectorstore = Pinecone(
                index=self.index,
                embedding_function=self.openai.embed_query,
                text_key="text",
                namespace="replica",
            )

        except Exception as e:
            BackLog.exception(instance=self, message=f"Exception occurred")

        self.initialized = True
        pass

    def match_product(self, messages: str):
        self.initialize()

        if self.vectorstore is None:
            return "Couldn't connect to pinecone vector db"

        docs = self.vectorstore.similarity_search(messages, k=1)
        if docs is not None and type(docs) == list and len(docs) > 0:
            return [docs[0].metadata["id"]]
        else:
            return "Nothing"

    def update_products(self, products_info, namespace):
        self.initialize()

        if self.vectorstore is None:
            return "Couldn't connect to pinecone vector db"

        batch = []
        for item in products_info["products"]:
            id = str(item["id"])
            value = self.openai.embed_query(item["label"])
            metadata = {"id": item["id"], "label": item["label"]}
            batch.append({"id": id, "values": value, "metadata": metadata})

        self.index.upsert(vectors=batch, namespace=namespace)
        # dataset = pd.DataFrame(products_info["products"])
        # meta = [{"id": x} for x in dataset["id"]]

        # self.vectorstore.add_texts(
        #     namespace=namespace, texts=dataset["label"], metadatas=meta
        # )

        BackLog.info(self, f"Import Done")
        pass


pinecone_service = PineconeService()
