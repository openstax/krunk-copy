from src.pages.base import PrivatePage

from selenium.webdriver.common.by import By


class ModuleImport(PrivatePage):
    _import_form_locator = (By.CSS_SELECTOR, 'form[action="module_import_form"][name="import"]')
    _import_file_field_locator = (By.CSS_SELECTOR, 'input[type="file"][name="importFile"]')

    @property
    def import_form(self):
        return self.find_element(*self._import_form_locator)

    @property
    def import_file_field(self):
        return self.import_form.find_element(*self._import_file_field_locator)

    def fill_in_filename(self, filename):
        self.import_file_field.send_keys(filename)
        return self

    def submit(self):
        self.import_form.submit()
        from src.pages.module_edit import ModuleEdit

        module_edit = ModuleEdit(self.driver, self.base_url, self.timeout)
        return module_edit.wait_for_page_to_load()
