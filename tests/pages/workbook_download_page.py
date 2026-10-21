import re

from playwright.sync_api import Download, Locator, Page

from tests.pages.base_page import BasePage, click_until_download


class WorkbookDownloadPage(BasePage):
    """The /download/{id} field-reordering and download page."""

    _MOVE_UP_RE = re.compile(r"^Move (.+) up$")

    def __init__(self, page: Page):
        super().__init__(page)
        self.heading = page.get_by_role("heading", name="Download Workbook:", exact=False)
        # "Back" is a comps.Button nested inside a rio.Link - matching on
        # visible text sidesteps any ambiguity in how that nesting exposes
        # roles.
        self.back_link = page.get_by_text("Back", exact=True)
        self.download_button = page.get_by_role("button", name="Download", exact=True)

    def move_up_button(self, field_name: str) -> Locator:
        return self.page.get_by_role("button", name=f"Move {field_name} up", exact=True)

    def move_down_button(self, field_name: str) -> Locator:
        return self.page.get_by_role("button", name=f"Move {field_name} down", exact=True)

    def field_order(self) -> list[str]:
        # Right after navigating here, the page's async on_populate (fetching
        # _fields_in_order) may not have finished yet - wait for the page to
        # have settled before reading, or this can race and return [].
        self.heading.wait_for(state="visible", timeout=10000)
        labels = [
            loc.get_attribute("aria-label")
            for loc in self.page.get_by_role(
                "button", name=self._MOVE_UP_RE
            ).all()
        ]
        return [self._MOVE_UP_RE.match(label).group(1) for label in labels if label]

    def move_field_up(self, field_name: str, attempts: int = 5) -> None:
        button = self.move_up_button(field_name)
        before = self.field_order()
        for _ in range(attempts):
            button.click(force=True)
            self.page.wait_for_timeout(200)
            if self.field_order() != before:
                return
        raise TimeoutError(f"Order did not change after clicking move-up for {field_name!r}")

    def move_field_down(self, field_name: str, attempts: int = 5) -> None:
        button = self.move_down_button(field_name)
        before = self.field_order()
        for _ in range(attempts):
            button.click(force=True)
            self.page.wait_for_timeout(200)
            if self.field_order() != before:
                return
        raise TimeoutError(f"Order did not change after clicking move-down for {field_name!r}")

    def download(self) -> Download:
        return click_until_download(self.page, self.download_button)

    def go_back(self) -> None:
        self.back_link.click(force=True)
