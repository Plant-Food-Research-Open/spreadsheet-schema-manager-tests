from playwright.sync_api import Download, Locator, Page

from tests.pages.base_page import BasePage, ConfirmDialog, click_until, click_until_closed, click_until_download, click_until_open, click_until_url_contains


class NameDialog:
    """The Name-only Save/Cancel dialog used for New/Rename/Save As across Templates and Workbooks."""

    def __init__(self, page: Page):
        self.page = page
        self.dialog = page.get_by_role("dialog")

    def fill_name(self, name: str) -> "NameDialog":
        self.dialog.get_by_role("textbox", name="Name").fill(name)
        return self

    def save(self) -> None:
        click_until_closed(self.dialog, self.page.get_by_text("Save", exact=True))

    def cancel(self) -> None:
        click_until_closed(self.dialog, self.page.get_by_text("Cancel", exact=True))


class WorkbooksListPageBase(BasePage):
    """Shared list view for Templates (/templates) and Workbooks (/workbooks) - both pages
    render via the app's WorkbooksPageBase, differing only in column set and per-row actions."""

    item_label = "item"

    def __init__(self, page: Page):
        super().__init__(page)
        self.add_button = page.get_by_role("button", name=f"Add {self.item_label}", exact=True)
        # Success/info banners render with role="status"; danger/warning
        # banners (e.g. validation errors) render with role="alert" instead
        # of "status" - never both at once. Match either.
        self.banner = page.locator('[role="status"], [role="alert"]')

    def item_link(self, name: str) -> Locator:
        return self.page.get_by_role("link", name=name, exact=True)

    def open_item(self, name: str) -> None:
        self.item_link(name).click()

    def rename_button(self, name: str) -> Locator:
        return self.page.get_by_role("button", name=f"Rename {name}", exact=True)

    def delete_button(self, name: str) -> Locator:
        return self.page.get_by_role("button", name=f"Delete {name}", exact=True)

    def open_add_dialog(self) -> NameDialog:
        dialog = NameDialog(self.page)
        click_until_open(dialog.dialog, self.add_button)
        return dialog

    def create(self, name: str) -> None:
        dialog = self.open_add_dialog()
        dialog.fill_name(name)
        dialog.save()

    def rename(self, old_name: str) -> NameDialog:
        dialog = NameDialog(self.page)
        click_until_open(dialog.dialog, self.rename_button(old_name))
        return dialog

    def delete(self, name: str) -> ConfirmDialog:
        confirm = ConfirmDialog(self.page)
        click_until_open(confirm.dialog, self.delete_button(name))
        return confirm


class TemplatesPage(WorkbooksListPageBase):
    path = "/templates"
    item_label = "template"
    item_type_name = "Template"

    def __init__(self, page: Page):
        super().__init__(page)
        self.heading = page.get_by_role(
            "heading", name="Templates (under your personal space)"
        )

    def new_workbook_button(self, template_name: str) -> Locator:
        return self.page.get_by_role("button", name=f"Create new workbook from {template_name}", exact=True)

    def create_workbook_from(self, template_name: str) -> NameDialog:
        dialog = NameDialog(self.page)
        click_until_open(dialog.dialog, self.new_workbook_button(template_name))
        return dialog


class WorkbooksPage(WorkbooksListPageBase):
    path = "/workbooks"
    item_label = "workbook"
    item_type_name = "Workbook"

    def __init__(self, page: Page):
        super().__init__(page)
        self.heading = page.get_by_role(
            "heading", name="Workbooks (under your personal space)"
        )

    def template_name_link(self, template_name: str) -> Locator:
        return self.page.get_by_role("link", name=template_name, exact=True)

    def download_workbook_button(self, name: str) -> Locator:
        return self.page.get_by_role("button", name=f"Download {name}", exact=True)

    def download_qr_button(self, name: str) -> Locator:
        return self.page.get_by_role("button", name=f"Download QR code for {name}", exact=True)

    def go_to_download_page(self, name: str) -> None:
        # "Download Workbook" navigates to the download/reorder page - it
        # doesn't trigger a file download itself.
        click_until_url_contains(self.page, self.download_workbook_button(name), "/download/")

    def download_qr(self, name: str) -> Download:
        return click_until_download(self.page, self.download_qr_button(name))
