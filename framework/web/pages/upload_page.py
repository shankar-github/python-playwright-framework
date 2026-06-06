"""File upload page object."""
from framework.web.base_page import BasePage


class UploadPage(BasePage):
    PATH = "/upload"

    FILE_INPUT_TEST_ID = "file-input"
    UPLOAD_BUTTON_TEST_ID = "upload-button"
    SUCCESS_TEST_ID = "upload-success"

    def open(self):
        self.navigate(self.PATH)

    def select_file(self, file_path: str):
        self.set_input_files_test_id(self.FILE_INPUT_TEST_ID, file_path)

    def submit(self):
        self.click_test_id(self.UPLOAD_BUTTON_TEST_ID)
        self.wait_for_test_id(self.SUCCESS_TEST_ID)

    def get_success_message(self) -> str:
        return self.get_text_test_id(self.SUCCESS_TEST_ID)
