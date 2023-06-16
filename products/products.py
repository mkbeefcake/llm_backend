class ProductService:
    def __init__(self) -> None:
        pass

    def get_bestseller_products(self):
        raise NotImplementedError

    def get_product_list(self):
        raise NotImplementedError

    def match_product(self, messages):
        raise NotImplementedError
