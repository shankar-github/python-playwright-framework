"""Page Object Model classes for web UI tests."""
from framework.web.pages.login_page import LoginPage
from framework.web.pages.registration_page import RegistrationPage
from framework.web.pages.products_page import ProductsPage
from framework.web.pages.contact_page import ContactPage
from framework.web.pages.upload_page import UploadPage
from framework.web.pages.home_page import HomePage

__all__ = [
    "LoginPage",
    "RegistrationPage",
    "ProductsPage",
    "ContactPage",
    "UploadPage",
    "HomePage",
]
