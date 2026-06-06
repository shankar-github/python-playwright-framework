"""Products page object."""
from framework.web.base_page import BasePage


class ProductsPage(BasePage):
    PATH = "/products"

    PRODUCT_ITEM_TEST_ID = "product-item"
    PRODUCT_NAME_TEST_ID = "product-name"
    PRODUCT_LIST_TEST_ID = "product-list"
    ADD_TO_CART_TEST_ID = "add-to-cart-button"
    CART_BADGE_TEST_ID = "cart-badge"
    SEARCH_INPUT_TEST_ID = "search-input"
    SEARCH_BUTTON_TEST_ID = "search-button"

    def open(self):
        self.navigate(self.PATH)

    def wait_for_products(self):
        self.wait_for_test_id(self.PRODUCT_LIST_TEST_ID)
        self.wait_for_load_state("domcontentloaded")

    def get_product_count(self) -> int:
        return len(self.locator_test_id(self.PRODUCT_ITEM_TEST_ID).all())

    def select_first_product(self) -> str:
        self.wait_for_test_id(self.PRODUCT_ITEM_TEST_ID)
        first_product = self.locator_test_id(self.PRODUCT_ITEM_TEST_ID).first
        product_name = first_product.get_by_test_id(self.PRODUCT_NAME_TEST_ID).inner_text()
        first_product.click()
        return product_name

    def add_to_cart(self):
        self.wait_for_test_id(self.ADD_TO_CART_TEST_ID)
        self.click_test_id(self.ADD_TO_CART_TEST_ID)

    def get_cart_count(self) -> str:
        self.wait_for_test_id(self.CART_BADGE_TEST_ID)
        return self.get_text_test_id(self.CART_BADGE_TEST_ID)

    def search(self, term: str):
        self.fill_test_id(self.SEARCH_INPUT_TEST_ID, term)
        self.click_test_id(self.SEARCH_BUTTON_TEST_ID)
        self.wait_for_test_id(self.PRODUCT_LIST_TEST_ID)
