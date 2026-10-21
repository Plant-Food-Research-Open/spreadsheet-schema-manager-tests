import pytest
from playwright.sync_api import expect

from tests.pages.base_page import pressable
from tests.pages.datasets_page import DatasetsPage
from utils.data_loader import data_file_path


@pytest.mark.smoke
def test_datasets_page_loads(datasets_page: DatasetsPage):
    expect(datasets_page.heading).to_be_visible()
    expect(datasets_page.add_button).to_be_visible()


@pytest.mark.regression
def test_upload_ready_dataset_shows_ready_status(datasets_page: DatasetsPage):
    datasets_page.upload(data_file_path("dataset_ready.csv"))

    expect(datasets_page.banner).to_contain_text("Dataset dataset_ready uploaded successfully.")
    expect(datasets_page.status_badge()).to_have_text("Ready")


@pytest.mark.regression
def test_upload_warning_dataset_shows_warning_status(datasets_page: DatasetsPage):
    datasets_page.upload(data_file_path("dataset_warning.csv"))

    expect(datasets_page.status_badge()).to_have_text("Warning")


@pytest.mark.regression
def test_upload_invalid_dataset_shows_invalid_status(datasets_page: DatasetsPage):
    datasets_page.upload(data_file_path("dataset_invalid.csv"))

    expect(datasets_page.status_badge()).to_have_text("Invalid")


@pytest.mark.regression
def test_upload_non_spreadsheet_file_shows_error_banner(datasets_page: DatasetsPage, tmp_path):
    path = tmp_path / "qa_bogus.xlsx"
    path.write_bytes(b"not a real xlsx file")
    datasets_page.upload(str(path))

    expect(datasets_page.banner).to_contain_text("is not a spreadsheet")


@pytest.mark.regression
def test_upload_with_no_file_shows_validation_banner(datasets_page: DatasetsPage):
    datasets_page.upload_with_no_file()

    expect(datasets_page.banner).to_contain_text("File name was not entered!")


@pytest.mark.regression
def test_rename_dataset_updates_name(datasets_page: DatasetsPage):
    datasets_page.upload(data_file_path("dataset_ready.csv"))

    dialog = datasets_page.rename("dataset_ready")
    dialog.fill_name("qa_new_name")
    dialog.save()

    expect(datasets_page.view_raw_button("qa_new_name")).to_be_visible()
    expect(datasets_page.view_raw_button("dataset_ready")).not_to_be_attached()
    expect(datasets_page.banner).to_contain_text("Dataset qa_new_name renamed successfully.")


@pytest.mark.regression
def test_delete_dataset_removes_row(datasets_page: DatasetsPage):
    datasets_page.upload(data_file_path("dataset_ready.csv"))

    confirm = datasets_page.delete("dataset_ready")
    expect(confirm.dialog).to_contain_text("Are you sure you want to delete dataset_ready?")
    confirm.confirm()

    expect(datasets_page.view_raw_button("dataset_ready")).not_to_be_attached()
    expect(datasets_page.banner).to_contain_text("Dataset dataset_ready deleted successfully.")


@pytest.mark.regression
def test_download_raw_triggers_file_download(datasets_page: DatasetsPage, tmp_path):
    datasets_page.upload(data_file_path("dataset_ready.csv"))

    download = datasets_page.download_raw("dataset_ready")
    save_path = tmp_path / "downloaded.csv"
    download.save_as(save_path)

    assert save_path.exists()


@pytest.mark.regression
def test_run_button_disabled_for_invalid_dataset(datasets_page: DatasetsPage):
    datasets_page.upload(data_file_path("dataset_invalid.csv"))

    expect(pressable(datasets_page.run_button("dataset_invalid"))).to_have_attribute(
        "aria-disabled", "true"
    )


@pytest.mark.regression
def test_standardised_actions_disabled_before_complete(datasets_page: DatasetsPage):
    datasets_page.upload(data_file_path("dataset_ready.csv"))

    expect(
        pressable(datasets_page.view_standardised_button("dataset_ready"))
    ).to_have_attribute("aria-disabled", "true")
    expect(
        pressable(datasets_page.download_standardised_button("dataset_ready"))
    ).to_have_attribute("aria-disabled", "true")
