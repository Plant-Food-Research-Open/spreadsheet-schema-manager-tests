import pytest
from playwright.sync_api import expect

from tests.pages.dataset_view_page import DatasetViewPage
from tests.pages.datasets_page import DatasetsPage
from utils.data_loader import data_file_path


def open_raw_view(datasets_page: DatasetsPage, name: str) -> DatasetViewPage:
    datasets_page.go_to_raw_view(name)
    return DatasetViewPage(datasets_page.page)


@pytest.mark.regression
def test_raw_view_shows_ready_status_and_tables(datasets_page: DatasetsPage):
    datasets_page.upload(data_file_path("dataset_ready.csv"))

    view = open_raw_view(datasets_page, "dataset_ready")

    expect(view.heading("Raw", "dataset_ready")).to_be_visible()
    expect(view.content()).to_contain_text(
        "No obvious errors found, please check the following detected types."
    )
    expect(view.tables).to_have_count(4)


@pytest.mark.regression
def test_raw_view_shows_warning_status_and_warnings_table(datasets_page: DatasetsPage):
    datasets_page.upload(data_file_path("dataset_warning.csv"))

    view = open_raw_view(datasets_page, "dataset_warning")

    expect(view.content()).to_contain_text(
        "Inconsistent field formats found, please check for potential typos."
    )
    expect(view.tables).to_have_count(5)


@pytest.mark.regression
def test_raw_view_shows_invalid_status_message(datasets_page: DatasetsPage):
    datasets_page.upload(data_file_path("dataset_invalid.csv"))

    view = open_raw_view(datasets_page, "dataset_invalid")

    expect(view.content()).to_contain_text("Error: no data found.")
    expect(view.tables).to_have_count(4)
