from playwright.sync_api import Download, Locator, Page

from tests.pages.base_page import (
    BasePage,
    ConfirmDialog,
    click_until_closed,
    click_until_download,
    click_until_open,
    click_until_url_contains,
)
from tests.pages.workbooks_page import NameDialog


class UploadDialog:
    """The 'Upload Dataset' dialog opened via DatasetsPage.add_button.

    Unlike NameDialog/NewFieldDialog, there is no Name textbox - the dataset
    name is derived from the uploaded file's own filename. Saving with no
    file chosen triggers the "File name was not entered!" validation banner.
    """

    def __init__(self, page: Page):
        self.page = page
        # Scoped by heading text, not a bare get_by_role("dialog"): saving a
        # multi-sheet xlsx immediately opens the "Select sheet" dialog before
        # this one has fully detached, so an unscoped locator can transiently
        # match both at once.
        self.dialog = page.get_by_role("dialog").filter(has_text="Upload Dataset")

    def choose_file(self, path: str) -> "UploadDialog":
        self.dialog.locator("input[type=file]").set_input_files(path)
        return self

    def save(self) -> None:
        click_until_closed(self.dialog, self.page.get_by_text("Save", exact=True))


class SheetSelectionDialog:
    """The 'Select sheet' dialog that follows saving a multi-sheet xlsx upload."""

    def __init__(self, page: Page):
        self.page = page
        self.dialog = page.get_by_role("dialog").filter(has_text="Select sheet")
        self.dropdown = self.dialog.get_by_role("combobox")
        self.ok_button = self.dialog.get_by_role("button", name="Ok", exact=True)

    def select_sheet(self, sheet_name: str) -> "SheetSelectionDialog":
        self.dropdown.click(force=True)
        option = self.page.get_by_role("option", name=sheet_name, exact=True)
        option.click()
        option.wait_for(state="hidden", timeout=2000)
        return self

    def confirm(self) -> None:
        click_until_closed(self.dialog, self.ok_button)


class DatasetsPage(BasePage):
    path = "/datasets"

    def __init__(self, page: Page):
        super().__init__(page)
        self.heading = page.get_by_role("heading", name="Datasets", exact=False)
        self.add_button = page.get_by_role("button", name="Add dataset", exact=True)
        # Success/info banners render with role="status"; danger/warning
        # banners (e.g. validation errors) render with role="alert" instead
        # of "status" - never both at once. Match either.
        self.banner = page.locator('[role="status"], [role="alert"]')

    def status_badge(self, index: int = 0) -> Locator:
        # ColoredStatus renders the status word ("Ready"/"Warning"/"Invalid"/
        # "Complete") inside a role="tooltip" element - positional, since
        # there's no per-row accessible name distinguishing which dataset.
        return self.page.get_by_role("tooltip").nth(index)

    def view_raw_button(self, name: str) -> Locator:
        return self.page.get_by_role("button", name=f"View {name}", exact=True)

    def download_raw_button(self, name: str) -> Locator:
        return self.page.get_by_role("button", name=f"Download {name}", exact=True)

    def run_button(self, name: str) -> Locator:
        return self.page.get_by_role("button", name=f"Run {name}", exact=True)

    def view_standardised_button(self, name: str) -> Locator:
        return self.page.get_by_role("button", name=f"View standardised {name}", exact=True)

    def download_standardised_button(self, name: str) -> Locator:
        return self.page.get_by_role(
            "button", name=f"Download standardised {name}", exact=True
        )

    def rename_button(self, name: str) -> Locator:
        return self.page.get_by_role("button", name=f"Rename {name}", exact=True)

    def delete_button(self, name: str) -> Locator:
        return self.page.get_by_role("button", name=f"Delete {name}", exact=True)

    def open_upload_dialog(self) -> UploadDialog:
        dialog = UploadDialog(self.page)
        click_until_open(dialog.dialog, self.add_button)
        return dialog

    def upload(self, path: str) -> None:
        dialog = self.open_upload_dialog()
        dialog.choose_file(path)
        dialog.save()

    def upload_with_no_file(self) -> None:
        dialog = self.open_upload_dialog()
        dialog.save()

    def upload_choosing_sheet(self, path: str, sheet_name: str) -> None:
        # Only multi-sheet spreadsheets trigger this second dialog - the app
        # infers the sheet automatically for single-sheet uploads.
        dialog = self.open_upload_dialog()
        dialog.choose_file(path)
        dialog.save()
        sheet_dialog = SheetSelectionDialog(self.page).select_sheet(sheet_name)
        sheet_dialog.confirm()

    def rename(self, old_name: str) -> NameDialog:
        dialog = NameDialog(self.page)
        click_until_open(dialog.dialog, self.rename_button(old_name))
        return dialog

    def delete(self, name: str) -> ConfirmDialog:
        confirm = ConfirmDialog(self.page)
        click_until_open(confirm.dialog, self.delete_button(name))
        return confirm

    def download_raw(self, name: str) -> Download:
        return click_until_download(self.page, self.download_raw_button(name))

    def download_standardised(self, name: str) -> Download:
        return click_until_download(self.page, self.download_standardised_button(name))

    def go_to_raw_view(self, name: str) -> None:
        click_until_url_contains(self.page, self.view_raw_button(name), "content=raw")

    def go_to_standardised_view(self, name: str) -> None:
        click_until_url_contains(
            self.page, self.view_standardised_button(name), "content=standardised"
        )

    def go_to_standardise_wizard(self, name: str) -> None:
        click_until_url_contains(self.page, self.run_button(name), "/standardise/")
