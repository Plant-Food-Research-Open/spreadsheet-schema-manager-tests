import pytest
from playwright.sync_api import Page, expect

from tests.pages.fields_page import FieldsPage
from tests.pages.workbook_detail_page import TemplateDetailPage, WorkbookDetailPage
from tests.pages.workbooks_page import TemplatesPage, WorkbooksPage

DETAIL_PAGE_CLASSES = [
    (TemplatesPage, TemplateDetailPage),
    (WorkbooksPage, WorkbookDetailPage),
]


@pytest.fixture(params=DETAIL_PAGE_CLASSES, ids=["template", "workbook"])
def list_and_detail_classes(request):
    return request.param


@pytest.fixture
def list_page(list_and_detail_classes, page: Page):
    list_cls, _ = list_and_detail_classes
    return list_cls(page).goto()


def open_detail(list_page, detail_cls, name: str):
    list_page.item_link(name).click()
    return detail_cls(list_page.page)


def go_to_list(list_page, list_cls) -> None:
    list_page.page.get_by_role(
        "link", name=list_cls.item_type_name + "s", exact=True
    ).click()


@pytest.mark.regression
def test_detail_page_loads(list_and_detail_classes, list_page):
    _, detail_cls = list_and_detail_classes
    list_page.create("QA Detail Load")

    detail = open_detail(list_page, detail_cls, "QA Detail Load")

    expect(detail.heading("QA Detail Load")).to_be_visible()
    expect(detail.save_button).to_be_visible()


@pytest.mark.regression
def test_save_shows_success_banner(list_and_detail_classes, list_page):
    _, detail_cls = list_and_detail_classes
    list_page.create("QA Save Success")

    detail = open_detail(list_page, detail_cls, "QA Save Success")
    detail.save()

    expect(detail.banner).to_contain_text(
        f"{detail_cls.item_label} QA Save Success saved successfully."
    )


@pytest.mark.regression
def test_field_checkbox_selection_persists_after_save(list_and_detail_classes, list_page):
    list_cls, detail_cls = list_and_detail_classes

    list_page.page.get_by_role("link", name="Fields", exact=True).click()
    FieldsPage(list_page.page).create_field("QA Checkbox Field", "Text")

    go_to_list(list_page, list_cls)
    list_page.create("QA Checkbox Item")
    detail = open_detail(list_page, detail_cls, "QA Checkbox Item")

    checkbox = detail.field_checkbox(0)
    expect(checkbox).not_to_be_checked()
    checkbox.click(force=True)
    detail.save()

    go_to_list(list_page, list_cls)
    detail = open_detail(list_page, detail_cls, "QA Checkbox Item")

    expect(detail.field_checkbox(0)).to_be_checked()


@pytest.mark.regression
def test_update_fields_pulls_in_newly_added_field(list_and_detail_classes, list_page):
    list_cls, detail_cls = list_and_detail_classes
    list_page.create("QA Update Fields Item")
    detail = open_detail(list_page, detail_cls, "QA Update Fields Item")

    list_page.page.get_by_role("link", name="Fields", exact=True).click()
    FieldsPage(list_page.page).create_field("QA New Field For Update", "Text")

    go_to_list(list_page, list_cls)
    detail = open_detail(list_page, detail_cls, "QA Update Fields Item")

    expect(detail.field_link("QA New Field For Update")).not_to_be_attached()

    detail.update_fields()

    expect(detail.banner).to_contain_text("Fields updated successfully.")
    expect(detail.field_link("QA New Field For Update")).to_be_visible()


@pytest.mark.regression
def test_type_filter_hides_non_matching_fields(list_and_detail_classes, list_page):
    list_cls, detail_cls = list_and_detail_classes

    list_page.page.get_by_role("link", name="Fields", exact=True).click()
    fields_page = FieldsPage(list_page.page)
    fields_page.create_field("QA Filter Text Field", "Text")
    fields_page.create_field("QA Filter Number Field", "Number")

    go_to_list(list_page, list_cls)
    list_page.create("QA Filter Item")
    detail = open_detail(list_page, detail_cls, "QA Filter Item")

    detail.toggle_type_filter("Text")

    expect(detail.field_link("QA Filter Text Field")).not_to_be_visible()
    expect(detail.field_link("QA Filter Number Field")).to_be_visible()


@pytest.mark.regression
def test_save_as_creates_copy(list_and_detail_classes, list_page):
    list_cls, detail_cls = list_and_detail_classes
    list_page.create("QA Save As Source")
    detail = open_detail(list_page, detail_cls, "QA Save As Source")

    detail.save_as("QA Save As Copy")

    expect(detail.banner).to_contain_text(
        f"{detail_cls.item_label} QA Save As Copy saved successfully."
    )

    go_to_list(list_page, list_cls)
    expect(list_page.item_link("QA Save As Copy")).to_be_visible()
    expect(list_page.item_link("QA Save As Source")).to_be_visible()


@pytest.mark.regression
def test_save_as_with_duplicate_name_shows_validation_banner(list_and_detail_classes, list_page):
    _, detail_cls = list_and_detail_classes
    list_page.create("QA Existing Name")
    list_page.create("QA Save As Dup Source")
    detail = open_detail(list_page, detail_cls, "QA Save As Dup Source")

    detail.save_as("QA Existing Name")

    expect(detail.banner).to_contain_text(
        f"{detail_cls.item_label} QA Existing Name already exists!"
    )


@pytest.mark.regression
def test_save_as_template_creates_template(workbooks_page: WorkbooksPage):
    workbooks_page.create("QA Save As Template Source")
    detail = open_detail(workbooks_page, WorkbookDetailPage, "QA Save As Template Source")

    detail.save_as_template("QA New Template From Workbook")

    expect(detail.banner).to_contain_text(
        "Template QA New Template From Workbook saved successfully."
    )

    detail.page.get_by_role("link", name="Templates", exact=True).click()
    templates_page = TemplatesPage(detail.page)
    expect(templates_page.item_link("QA New Template From Workbook")).to_be_visible()


@pytest.mark.regression
def test_download_workbook_button_navigates_to_download_page(workbooks_page: WorkbooksPage):
    workbooks_page.create("QA Detail Download Nav")
    detail = open_detail(workbooks_page, WorkbookDetailPage, "QA Detail Download Nav")

    detail.go_to_download_page()

    expect(
        detail.page.get_by_role(
            "heading", name="Download Workbook: QA Detail Download Nav"
        )
    ).to_be_visible()
