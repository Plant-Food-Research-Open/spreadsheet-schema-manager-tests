from playwright.sync_api import Download, Locator, Page

from tests.pages.base_page import BasePage, ConfirmDialog, TypeFilterMixin, click_until_closed, click_until_open


class NewFieldDialog:
    """The 'New Field' dialog opened via FieldsPage.add_field_button."""

    def __init__(self, page: Page):
        self.page = page
        self.dialog = page.get_by_role("dialog")

    def fill_name(self, name: str) -> "NewFieldDialog":
        self.dialog.get_by_role("textbox", name="Name").fill(name)
        return self

    def select_type(self, field_type: str) -> "NewFieldDialog":
        self.dialog.get_by_role("textbox", name="Field type").click()
        option = self.page.get_by_role("option", name=field_type, exact=True)
        option.click()
        option.wait_for(state="hidden", timeout=2000)
        return self

    def save(self) -> None:
        click_until_closed(self.dialog, self.page.get_by_text("Save", exact=True))

    def cancel(self) -> None:
        click_until_closed(self.dialog, self.page.get_by_text("Cancel", exact=True))


class RenameFieldDialog:
    """The 'Rename Field' dialog opened via FieldsPage.rename_button."""

    def __init__(self, page: Page):
        self.page = page
        self.dialog = page.get_by_role("dialog")

    def fill_name(self, name: str) -> "RenameFieldDialog":
        self.dialog.get_by_role("textbox", name="Name").fill(name)
        return self

    def save(self) -> None:
        click_until_closed(self.dialog, self.page.get_by_text("Save", exact=True))

    def cancel(self) -> None:
        click_until_closed(self.dialog, self.page.get_by_text("Cancel", exact=True))


class ImportDialog:
    """The 'Import Field Definitions from File' dialog."""

    def __init__(self, page: Page):
        self.page = page
        self.dialog = page.get_by_role("dialog")

    def choose_file(self, path: str) -> "ImportDialog":
        self.dialog.locator("input[type=file]").set_input_files(path)
        return self

    def save(self) -> None:
        click_until_closed(self.dialog, self.dialog.get_by_text("Save", exact=True))


class FieldsPage(BasePage, TypeFilterMixin):
    path = "/fields"

    def __init__(self, page: Page):
        super().__init__(page)
        self.heading = page.get_by_role(
            "heading", name="Fields (under your personal space)"
        )
        self.export_button = page.get_by_role("button", name="Export")
        self.import_button = page.get_by_role("button", name="Import")
        self.delete_all_button = page.get_by_role("button", name="Delete All")
        self.group_filter_button = page.get_by_role("button", name="Group")
        self.type_filter_button = page.get_by_role("button", name="Type")
        self.add_field_button = page.get_by_role("button", name="Add field")
        # Success/info banners render with role="status"; danger/warning
        # banners (e.g. validation errors) render with role="alert" instead
        # of "status" - never both at once. Match either.
        self.banner = page.locator('[role="status"], [role="alert"]')

    def field_link(self, name: str) -> Locator:
        return self.page.get_by_role("link", name=name, exact=True)

    def open_field(self, name: str) -> None:
        self.field_link(name).click()

    def delete_button(self, name: str) -> Locator:
        return self.page.get_by_role("button", name=f"Delete {name}")

    def rename_button(self, name: str) -> Locator:
        return self.page.get_by_role("button", name=f"Rename {name}")

    def open_add_field_dialog(self) -> NewFieldDialog:
        dialog = NewFieldDialog(self.page)
        click_until_open(dialog.dialog, self.add_field_button)
        return dialog

    def create_field(self, name: str, field_type: str) -> None:
        dialog = self.open_add_field_dialog()
        dialog.fill_name(name).select_type(field_type)
        dialog.save()

    def rename_field(self, name: str) -> RenameFieldDialog:
        dialog = RenameFieldDialog(self.page)
        click_until_open(dialog.dialog, self.rename_button(name))
        return dialog

    def delete_field(self, name: str) -> ConfirmDialog:
        confirm = ConfirmDialog(self.page)
        click_until_open(confirm.dialog, self.delete_button(name))
        return confirm

    def open_delete_all_confirm(self) -> ConfirmDialog:
        confirm = ConfirmDialog(self.page)
        click_until_open(confirm.dialog, self.delete_all_button)
        return confirm

    def export(self) -> Download:
        with self.page.expect_download() as download_info:
            self.export_button.click(force=True)
        return download_info.value

    def open_import_dialog(self) -> ImportDialog:
        dialog = ImportDialog(self.page)
        click_until_open(dialog.dialog, self.import_button)
        return dialog

    def back_from_import_summary(self) -> None:
        self.page.get_by_role("button", name="Back").click(force=True)
