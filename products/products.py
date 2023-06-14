from abc import abstractmethod


class ProductService:
    def __init__(self) -> None:
        pass

    @abstractmethod
    def get_bestseller_products(self):
        raise NotImplementedError

    @abstractmethod
    def get_product_list(self):
        raise NotImplementedError

    @abstractmethod
    def match_product(self, messages):
        raise NotImplementedError
