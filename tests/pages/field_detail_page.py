from playwright.sync_api import Locator, Page

from tests.pages.base_page import BasePage, click_until


class FieldDetailPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.group_field = page.get_by_role("textbox", name="Group")
        self.description_field = page.get_by_role("textbox", name="Description")
        self.reference_url_field = page.get_by_role("textbox", name="Reference URL")
        self.trait_field = page.get_by_role("textbox", name="Trait")
        self.unit_field = page.get_by_role("textbox", name="Unit")
        self.method_field = page.get_by_role("textbox", name="Method")
        self.save_button = page.get_by_role("button", name="Save Field")
        self.add_item_button = page.get_by_role("button", name="Add item")
        # Success/info banners render with role="status"; danger/warning
        # banners (e.g. validation errors) render with role="alert" instead
        # of "status" - never both at once. Match either.
        self.banner = page.locator('[role="status"], [role="alert"]')

    def heading(self, field_type: str, name: str) -> Locator:
        return self.page.get_by_role("heading", name=f"{field_type} Field: {name}")

    def save(self) -> None:
        click_until(self.banner, self.save_button, "visible")

    def add_item(self) -> None:
        existing_rows = self.page.get_by_role(
            "button", name="Delete row", exact=False
        ).count()
        next_row_button = self.delete_row_button(existing_rows + 1)
        click_until(next_row_button, self.add_item_button, "visible")

    def value_header_input(self, index: int = 0) -> Locator:
        return self.page.get_by_label("Value Header").nth(index)

    def value_description_input(self, index: int = 0) -> Locator:
        return self.page.get_by_label("Value Description").nth(index)

    def parameter_input(self, index: int = 0) -> Locator:
        return self.page.get_by_label("Parameter").nth(index)

    def value_input(self, index: int = 0) -> Locator:
        return self.page.get_by_label("Value").nth(index)

    def delete_row_button(self, row_number: int) -> Locator:
        return self.page.get_by_role("button", name=f"Delete row {row_number}")

    def delete_first_value_row(self, attempts: int = 5) -> None:
        # The row-deletion handler is a synchronous local mutation, but a
        # rapid second click can land mid-re-render and silently no-op - use
        # an actual row-count check to confirm each deletion, not just a wait.
        rows = self.page.get_by_role("button", name="Delete row", exact=False)
        rows.first.wait_for(state="visible", timeout=10000)
        before = rows.count()
        for _ in range(attempts):
            self.delete_row_button(1).click(force=True)
            self.page.wait_for_timeout(400)
            if rows.count() == before - 1:
                return
        raise TimeoutError("Deleting the first value row did not reduce the row count")
