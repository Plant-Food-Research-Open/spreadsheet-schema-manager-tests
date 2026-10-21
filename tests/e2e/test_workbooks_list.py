import pytest
from playwright.sync_api import Page, expect

from tests.pages.workbooks_page import TemplatesPage, WorkbooksPage

LIST_PAGE_CLASSES = [TemplatesPage, WorkbooksPage]


@pytest.fixture(params=LIST_PAGE_CLASSES, ids=["templates", "workbooks"])
def list_page(request, page: Page):
    return request.param(page).goto()


@pytest.mark.smoke
def test_list_page_loads(list_page):
    expect(list_page.heading).to_be_visible()
    expect(list_page.add_button).to_be_visible()


@pytest.mark.regression
def test_create_item_appears_in_table(list_page):
    list_page.create("QA New Item")

    expect(list_page.item_link("QA New Item")).to_be_visible()
    expect(list_page.rename_button("QA New Item")).to_be_visible()
    expect(list_page.banner).to_contain_text(
        f"{list_page.item_type_name} QA New Item created successfully."
    )


@pytest.mark.regression
def test_create_item_with_empty_name_shows_validation_banner(list_page):
    dialog = list_page.open_add_dialog()
    dialog.fill_name("")
    dialog.save()

    expect(list_page.banner).to_contain_text(
        f"{list_page.item_type_name} name was not entered!"
    )


@pytest.mark.regression
def test_create_item_with_duplicate_name_shows_validation_banner(list_page):
    list_page.create("QA Duplicate")

    dialog = list_page.open_add_dialog()
    dialog.fill_name("QA Duplicate")
    dialog.save()

    expect(list_page.banner).to_contain_text(
        f"{list_page.item_type_name} QA Duplicate already exists!"
    )


@pytest.mark.regression
def test_cancel_create_dialog_does_not_create_item(list_page):
    dialog = list_page.open_add_dialog()
    dialog.fill_name("QA Cancelled")
    dialog.cancel()

    expect(list_page.item_link("QA Cancelled")).not_to_be_attached()


@pytest.mark.regression
def test_rename_item_updates_name(list_page):
    list_page.create("QA Old Name")

    dialog = list_page.rename("QA Old Name")
    dialog.fill_name("QA New Name")
    dialog.save()

    expect(list_page.item_link("QA New Name")).to_be_visible()
    expect(list_page.item_link("QA Old Name")).not_to_be_attached()
    expect(list_page.banner).to_contain_text(
        f"{list_page.item_type_name} QA New Name renamed successfully."
    )


@pytest.mark.regression
def test_rename_item_to_duplicate_name_shows_validation_banner(list_page):
    list_page.create("QA Keep Name")
    list_page.create("QA Other Name")

    dialog = list_page.rename("QA Other Name")
    dialog.fill_name("QA Keep Name")
    dialog.save()

    expect(list_page.banner).to_contain_text(
        f"{list_page.item_type_name} QA Keep Name already exists!"
    )


@pytest.mark.regression
def test_delete_item_removes_only_that_row(list_page):
    list_page.create("QA Keep Me")
    list_page.create("QA Remove Me")

    confirm = list_page.delete("QA Remove Me")
    expect(confirm.dialog).to_contain_text("Are you sure you want to delete QA Remove Me?")
    confirm.confirm()

    expect(list_page.item_link("QA Remove Me")).not_to_be_attached()
    expect(list_page.item_link("QA Keep Me")).to_be_visible()
    expect(list_page.banner).to_contain_text(
        f"{list_page.item_type_name} QA Remove Me deleted successfully."
    )


@pytest.mark.regression
def test_delete_item_dismiss_confirm_keeps_item(list_page):
    list_page.create("QA Dismiss Delete")

    confirm = list_page.delete("QA Dismiss Delete")
    confirm.dismiss()

    expect(list_page.item_link("QA Dismiss Delete")).to_be_visible()


@pytest.fixture
def templates_page(page: Page) -> TemplatesPage:
    return TemplatesPage(page).goto()


@pytest.mark.regression
def test_new_workbook_from_template_navigates_to_workbook_detail(templates_page: TemplatesPage):
    templates_page.create("QA Source Template")

    dialog = templates_page.create_workbook_from("QA Source Template")
    dialog.fill_name("QA New Workbook")
    dialog.save()

    expect(
        templates_page.page.get_by_role("heading", name="Workbook: QA New Workbook")
    ).to_be_visible()


@pytest.mark.regression
def test_workbook_shows_source_template_link(templates_page: TemplatesPage):
    templates_page.create("QA Link Template")
    dialog = templates_page.create_workbook_from("QA Link Template")
    dialog.fill_name("QA Link Workbook")
    dialog.save()

    templates_page.page.get_by_role("link", name="Workbooks", exact=True).click()
    workbooks_page = WorkbooksPage(templates_page.page)

    expect(workbooks_page.item_link("QA Link Workbook")).to_be_visible()
    expect(workbooks_page.template_name_link("QA Link Template")).to_be_visible()


@pytest.mark.regression
def test_download_workbook_navigates_to_download_page(workbooks_page: WorkbooksPage):
    workbooks_page.create("QA Download Workbook")
    workbooks_page.go_to_download_page("QA Download Workbook")

    expect(
        workbooks_page.page.get_by_role(
            "heading", name="Download Workbook: QA Download Workbook"
        )
    ).to_be_visible()


@pytest.mark.regression
def test_download_qr_triggers_file_download(workbooks_page: WorkbooksPage, tmp_path):
    workbooks_page.create("QA QR Workbook")

    download = workbooks_page.download_qr("QA QR Workbook")
    save_path = tmp_path / "qr.xlsx"
    download.save_as(save_path)

    assert save_path.exists()
