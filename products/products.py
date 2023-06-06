from abc import abstractmethod


class ProductService:
    def __init__(self) -> None:
        pass

    @abstractmethod
    async def get_bestseller_products(self):
        raise NotImplementedError

    @abstractmethod
    async def get_product_list(self):
        raise NotImplementedError
