import pytest
from playwright.sync_api import expect

from tests.pages.fields_page import FieldsPage


@pytest.mark.smoke
def test_fields_page_loads(fields_page: FieldsPage):
    expect(fields_page.heading).to_be_visible()
    expect(fields_page.export_button).to_be_visible()
    expect(fields_page.import_button).to_be_visible()
    expect(fields_page.delete_all_button).to_be_visible()
    expect(fields_page.group_filter_button).to_be_visible()
    expect(fields_page.type_filter_button).to_be_visible()
    expect(fields_page.add_field_button).to_be_visible()


@pytest.mark.regression
def test_create_field_appears_in_table(fields_page: FieldsPage):
    fields_page.create_field("QA Text Field", "Text")

    expect(fields_page.field_link("QA Text Field")).to_be_visible()
    expect(fields_page.delete_button("QA Text Field")).to_be_visible()
    expect(fields_page.banner).to_contain_text(
        "Field QA Text Field created successfully."
    )


@pytest.mark.regression
def test_rename_field_updates_name(fields_page: FieldsPage):
    fields_page.create_field("Old Name", "Text")

    dialog = fields_page.rename_field("Old Name")
    dialog.fill_name("New Name").save()

    expect(fields_page.field_link("New Name")).to_be_visible()
    expect(fields_page.field_link("Old Name")).not_to_be_attached()
    expect(fields_page.banner).to_contain_text("Field New Name renamed successfully.")


@pytest.mark.regression
def test_delete_field_removes_only_that_row(fields_page: FieldsPage):
    fields_page.create_field("Keep Me", "Text")
    fields_page.create_field("Remove Me", "Number")

    confirm = fields_page.delete_field("Remove Me")
    expect(confirm.dialog).to_contain_text("Are you sure you want to delete Remove Me?")
    confirm.confirm()

    expect(fields_page.field_link("Remove Me")).not_to_be_attached()
    expect(fields_page.field_link("Keep Me")).to_be_visible()
    expect(fields_page.banner).to_contain_text("Field Remove Me deleted successfully.")


@pytest.mark.regression
def test_delete_all_clears_every_field(fields_page: FieldsPage):
    fields_page.create_field("Bulk A", "Text")
    fields_page.create_field("Bulk B", "Number")

    confirm = fields_page.open_delete_all_confirm()
    expect(confirm.dialog).to_contain_text("Are you sure you want to delete all fields?")
    confirm.confirm()

    expect(fields_page.field_link("Bulk A")).not_to_be_attached()
    expect(fields_page.field_link("Bulk B")).not_to_be_attached()
    expect(fields_page.banner).to_contain_text("All Fields deleted successfully.")


@pytest.mark.regression
def test_type_filter_hides_non_matching_fields(fields_page: FieldsPage):
    fields_page.create_field("Filter Text Field", "Text")
    fields_page.create_field("Filter Number Field", "Number")

    fields_page.toggle_type_filter("Text")

    expect(fields_page.field_link("Filter Text Field")).not_to_be_visible()
    expect(fields_page.field_link("Filter Number Field")).to_be_visible()


@pytest.mark.regression
def test_export_then_import_restores_fields(fields_page: FieldsPage, tmp_path):
    fields_page.create_field("Round Trip A", "Text")
    fields_page.create_field("Round Trip B", "Date")

    download = fields_page.export()
    export_path = tmp_path / "Fields.xlsx"
    download.save_as(export_path)

    fields_page.open_delete_all_confirm().confirm()
    expect(fields_page.field_link("Round Trip A")).not_to_be_attached()

    import_dialog = fields_page.open_import_dialog()
    import_dialog.choose_file(str(export_path))
    import_dialog.save()

    expect(fields_page.page.get_by_text("2 detected fields", exact=False)).to_be_visible()
    fields_page.back_from_import_summary()

    expect(fields_page.field_link("Round Trip A")).to_be_visible()
    expect(fields_page.field_link("Round Trip B")).to_be_visible()


@pytest.mark.regression
def test_import_rejects_non_spreadsheet_file(fields_page: FieldsPage, tmp_path):
    bogus_file = tmp_path / "not-a-spreadsheet.xlsx"
    bogus_file.write_text("this is not a real xlsx file")

    import_dialog = fields_page.open_import_dialog()
    import_dialog.choose_file(str(bogus_file))
    import_dialog.save()

    expect(fields_page.banner).to_contain_text("is not a spreadsheet")
