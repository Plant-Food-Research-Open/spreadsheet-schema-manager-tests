from playwright.sync_api import Locator, Page

from tests.pages.base_page import BasePage


class DatasetViewPage(BasePage):
    """The /datasets/{id}?content=raw|standardised validation-report page."""

    def __init__(self, page: Page):
        super().__init__(page)
        # rio.Table has no built-in accessible row/cell structure; the app
        # sets accessibility_role="table" on the container so each table is
        # at least individually locatable, even without row/cell semantics.
        self.tables = page.get_by_role("table")

    def heading(self, prefix: str, name: str) -> Locator:
        return self.page.get_by_role("heading", name=f"{prefix} Dataset: {name}")

    def content(self) -> Locator:
        return self.page.get_by_role("main")
