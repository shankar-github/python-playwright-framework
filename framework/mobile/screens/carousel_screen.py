"""Carousel screen object."""
from framework.mobile.base_screen import BaseScreen


class CarouselScreen(BaseScreen):
    APP_ID = "com.example.app:id"

    CAROUSEL_TAB = f"{APP_ID}/carousel_tab"
    CAROUSEL_VIEW = f"{APP_ID}/carousel_view"

    def open(self):
        self.click("id", self.CAROUSEL_TAB)
        self.wait_for_element("id", self.CAROUSEL_VIEW)

    def swipe_next(self):
        self.swipe_up()

    def swipe_previous(self):
        self.swipe_down()
