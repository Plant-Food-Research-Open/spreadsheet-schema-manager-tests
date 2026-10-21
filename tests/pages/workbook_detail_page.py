from playwright.sync_api import Locator, Page

from tests.pages.base_page import BasePage, TypeFilterMixin, click_until, click_until_download, click_until_open, click_until_url_contains
from tests.pages.workbooks_page import NameDialog


class WorkbookDetailPageBase(BasePage, TypeFilterMixin):
    """Shared detail view for Templates (/templates/{id}) and Workbooks (/workbooks/{id}) -
    both render via the app's WorkbookPageBase, differing only in the item label and the
    Workbook-only Save As Template/Download actions."""

    item_label = "Item"

    def __init__(self, page: Page):
        super().__init__(page)
        self.save_button = page.get_by_role("button", name=f"Save {self.item_label}", exact=True)
        self.save_as_button = page.get_by_role("button", name=f"Save {self.item_label} As...", exact=True)
        self.update_fields_button = page.get_by_role("button", name="Update Fields", exact=True)
        self.group_filter_button = page.get_by_role("button", name="Group", exact=True)
        self.type_filter_button = page.get_by_role("button", name="Type", exact=True)
        # Success/info banners render with role="status"; danger/warning
        # banners (e.g. validation errors) render with role="alert" instead
        # of "status" - never both at once. Match either.
        self.banner = page.locator('[role="status"], [role="alert"]')

    def heading(self, name: str) -> Locator:
        return self.page.get_by_role("heading", name=f"{self.item_label}: {name}")

    def field_link(self, name: str) -> Locator:
        return self.page.get_by_role("link", name=name, exact=True)

    def field_checkbox(self, index: int = 0) -> Locator:
        # The field-selection table renders as one flat CSS grid with no
        # per-row DOM wrapper, so rows aren't scopable by ancestry - target
        # by position instead, matching field creation/row order.
        return self.page.get_by_role("checkbox").nth(index)

    def save(self) -> None:
        click_until(self.banner, self.save_button, "visible")

    def open_save_as_dialog(self) -> NameDialog:
        dialog = NameDialog(self.page)
        click_until_open(dialog.dialog, self.save_as_button)
        return dialog

    def save_as(self, name: str) -> None:
        dialog = self.open_save_as_dialog()
        dialog.fill_name(name)
        dialog.save()

    def update_fields(self) -> None:
        click_until(self.banner, self.update_fields_button, "visible")


class TemplateDetailPage(WorkbookDetailPageBase):
    item_label = "Template"


class WorkbookDetailPage(WorkbookDetailPageBase):
    item_label = "Workbook"

    def __init__(self, page: Page):
        super().__init__(page)
        self.save_as_template_button = page.get_by_role("button", name="Save As Template...", exact=True)
        self.download_workbook_button = page.get_by_role("button", name="Download Workbook", exact=True)
        self.download_qr_button = page.get_by_role("button", name="Download QRCode", exact=True)

    def open_save_as_template_dialog(self) -> NameDialog:
        dialog = NameDialog(self.page)
        click_until_open(dialog.dialog, self.save_as_template_button)
        return dialog

    def save_as_template(self, name: str) -> None:
        dialog = self.open_save_as_template_dialog()
        dialog.fill_name(name)
        dialog.save()

    def go_to_download_page(self) -> None:
        # Navigates to /download/{id} - it doesn't trigger a file download itself.
        click_until_url_contains(self.page, self.download_workbook_button, "/download/")

    def download_qr(self):
        return click_until_download(self.page, self.download_qr_button)
