"""App navigation screen object."""
from framework.mobile.base_screen import BaseScreen


class NavigationScreen(BaseScreen):
    APP_ID = "com.example.app:id"

    HOME_TAB = f"{APP_ID}/home_tab"
    HOME_SCREEN = f"{APP_ID}/home_screen"
    PRODUCTS_TAB = f"{APP_ID}/products_tab"
    PRODUCTS_SCREEN = f"{APP_ID}/products_screen"
    PROFILE_TAB = f"{APP_ID}/profile_tab"
    PROFILE_SCREEN = f"{APP_ID}/profile_screen"

    def go_to_home(self):
        self.click("id", self.HOME_TAB)
        self.wait_for_element("id", self.HOME_SCREEN)

    def go_to_products(self):
        self.click("id", self.PRODUCTS_TAB)
        self.wait_for_element("id", self.PRODUCTS_SCREEN)

    def go_to_profile(self):
        self.click("id", self.PROFILE_TAB)
        self.wait_for_element("id", self.PROFILE_SCREEN)

    def press_android_back(self):
        self.press_keycode(4)

    def wait_for_products_screen(self):
        self.wait_for_element("id", self.PRODUCTS_SCREEN)
