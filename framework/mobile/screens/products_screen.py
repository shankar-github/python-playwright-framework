"""Products screen object."""
from framework.mobile.base_screen import BaseScreen


class ProductsScreen(BaseScreen):
    APP_ID = "com.example.app:id"

    PRODUCTS_TAB = f"{APP_ID}/products_tab"
    PRODUCT_LIST = f"{APP_ID}/product_list"
    PRODUCT_ITEM = f"{APP_ID}/product_item"
    FILTER_BUTTON = f"{APP_ID}/filter_button"
    FILTER_DIALOG = f"{APP_ID}/filter_dialog"
    CATEGORY_FILTER = f"{APP_ID}/category_filter"
    APPLY_FILTER_BUTTON = f"{APP_ID}/apply_filter_button"

    def open(self):
        self.click("id", self.PRODUCTS_TAB)
        self.wait_for_element("id", self.PRODUCT_LIST)

    def swipe_through_list(self):
        self.swipe_down()

    def get_product_count(self) -> int:
        return len(self.find_elements("id", self.PRODUCT_ITEM))

    def apply_category_filter(self):
        self.click("id", self.FILTER_BUTTON)
        self.wait_for_element("id", self.FILTER_DIALOG)
        self.click("id", self.CATEGORY_FILTER)
        self.click("id", self.APPLY_FILTER_BUTTON)
        self.wait_for_element("id", self.PRODUCT_LIST)
