import openpyxl
import pytest
from playwright.sync_api import expect

from tests.pages.fields_page import FieldsPage
from tests.pages.workbook_detail_page import WorkbookDetailPage
from tests.pages.workbook_download_page import WorkbookDownloadPage
from tests.pages.workbooks_page import WorkbooksPage


def open_download_page(workbooks_page: WorkbooksPage, name: str) -> WorkbookDownloadPage:
    workbooks_page.item_link(name).click()
    detail = WorkbookDetailPage(workbooks_page.page)
    detail.go_to_download_page()
    return WorkbookDownloadPage(workbooks_page.page)


@pytest.mark.regression
def test_download_page_lists_only_selected_fields_in_order(workbooks_page: WorkbooksPage):
    workbooks_page.page.get_by_role("link", name="Fields", exact=True).click()
    fields_page = FieldsPage(workbooks_page.page)
    fields_page.create_field("QA Download Field A", "Text")
    fields_page.create_field("QA Download Field B", "Text")

    workbooks_page.page.get_by_role("link", name="Workbooks", exact=True).click()
    workbooks_page.create("QA Download Order Workbook")
    workbooks_page.item_link("QA Download Order Workbook").click()
    detail = WorkbookDetailPage(workbooks_page.page)
    detail.field_checkbox(0).click(force=True)
    detail.field_checkbox(1).click(force=True)
    detail.save()
    detail.go_to_download_page()

    download_page = WorkbookDownloadPage(workbooks_page.page)
    expect(download_page.heading).to_be_visible()
    assert download_page.field_order() == ["QA Download Field A", "QA Download Field B"]


@pytest.mark.regression
def test_reorder_fields_up_down_changes_order(workbooks_page: WorkbooksPage):
    workbooks_page.page.get_by_role("link", name="Fields", exact=True).click()
    fields_page = FieldsPage(workbooks_page.page)
    fields_page.create_field("QA Reorder Field A", "Text")
    fields_page.create_field("QA Reorder Field B", "Text")

    workbooks_page.page.get_by_role("link", name="Workbooks", exact=True).click()
    workbooks_page.create("QA Reorder Workbook")
    workbooks_page.item_link("QA Reorder Workbook").click()
    detail = WorkbookDetailPage(workbooks_page.page)
    detail.field_checkbox(0).click(force=True)
    detail.field_checkbox(1).click(force=True)
    detail.save()
    detail.go_to_download_page()

    download_page = WorkbookDownloadPage(workbooks_page.page)
    assert download_page.field_order() == ["QA Reorder Field A", "QA Reorder Field B"]

    download_page.move_field_down("QA Reorder Field A")

    assert download_page.field_order() == ["QA Reorder Field B", "QA Reorder Field A"]


@pytest.mark.regression
def test_back_button_returns_to_workbook_page(workbooks_page: WorkbooksPage):
    workbooks_page.create("QA Download Back")
    download_page = open_download_page(workbooks_page, "QA Download Back")

    download_page.go_back()

    expect(
        workbooks_page.page.get_by_role("heading", name="Workbook: QA Download Back")
    ).to_be_visible()


@pytest.mark.regression
def test_download_triggers_file_download(workbooks_page: WorkbooksPage, tmp_path):
    workbooks_page.create("QA Download Trigger")
    download_page = open_download_page(workbooks_page, "QA Download Trigger")

    download = download_page.download()
    save_path = tmp_path / "workbook.xlsx"
    download.save_as(save_path)

    assert save_path.exists()


@pytest.mark.regression
def test_date_field_column_gets_iso_date_format(workbooks_page: WorkbooksPage, tmp_path):
    workbooks_page.page.get_by_role("link", name="Fields", exact=True).click()
    fields_page = FieldsPage(workbooks_page.page)
    fields_page.create_field("QA Date Format Field", "Date")

    workbooks_page.page.get_by_role("link", name="Workbooks", exact=True).click()
    workbooks_page.create("QA Date Format Workbook")
    workbooks_page.item_link("QA Date Format Workbook").click()
    detail = WorkbookDetailPage(workbooks_page.page)
    detail.field_checkbox(0).click(force=True)
    detail.save()
    detail.go_to_download_page()

    download_page = WorkbookDownloadPage(workbooks_page.page)
    download = download_page.download()
    save_path = tmp_path / "date_format_workbook.xlsx"
    download.save_as(save_path)

    wb = openpyxl.load_workbook(save_path)
    raw_sheet = wb["RawData"]
    assert raw_sheet["A1"].value == "QA Date Format Field"
    assert raw_sheet.column_dimensions["A"].number_format == "yyyy-mm-dd"
