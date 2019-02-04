from src.regions.base import Region
from src.pages.workspace import Workspace

from selenium.webdriver.common.by import By


class WorkspaceCollection(Workspace):
    _collection_locator = (By.CSS_SELECTOR, "tr.odd, tr.even")

    def remove(self):
        self.remove_button.click()
        from pages.legacy.collections_confirm_remove import CollectionsConfirmRemove

        confirm_remove = CollectionsConfirmRemove(self.driver, self.base_url, self.timeout)
        return confirm_remove.wait_for_page_to_load()

    @property
    def collection_list(self):
        return [
            self.WorkspaceCollectionEdit(self, el)
            for el in self.find_elements(*self._collection_locator)
        ]

    class WorkspaceCollectionEdit(Region):
        _link_locator = (By.CSS_SELECTOR, ".visualIcon > a")
        _id_locator = (By.CSS_SELECTOR, "td:nth-child(3)")

        def click_collection_link(self):
            self.find_element(*self._link_locator).click()
            from src.pages.collection_edit import CollectionEdit

            return CollectionEdit(
                self.driver, self.page.base_url, self.page.timeout
            ).wait_for_page_to_load()

        @property
        def collection_id(self):
            return self.find_element(*self._id_locator).text
