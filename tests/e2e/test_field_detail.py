import pytest
from playwright.sync_api import expect

from tests.pages.field_detail_page import FieldDetailPage
from tests.pages.fields_page import FieldsPage

ALL_TYPES = ["Category", "Measurement", "Text", "Number", "Date"]


def open_detail(fields_page: FieldsPage, name: str) -> FieldDetailPage:
    fields_page.open_field(name)
    return FieldDetailPage(fields_page.page)


@pytest.mark.regression
@pytest.mark.parametrize("field_type", ALL_TYPES)
def test_field_link_opens_detail_page(fields_page: FieldsPage, field_type: str):
    name = f"Detail Nav {field_type}"
    fields_page.create_field(name, field_type)

    detail = open_detail(fields_page, name)

    expect(detail.heading(field_type, name)).to_be_visible()


@pytest.mark.regression
@pytest.mark.parametrize("field_type", ALL_TYPES)
def test_common_fields_persist_after_save(fields_page: FieldsPage, field_type: str):
    name = f"Detail Save {field_type}"
    fields_page.create_field(name, field_type)

    detail = open_detail(fields_page, name)
    detail.group_field.fill("QA Group")
    detail.description_field.fill("QA description text")
    detail.reference_url_field.fill("https://example.com/qa")
    detail.save()

    expect(detail.banner).to_contain_text(f"Field {name} saved successfully.")
    expect(detail.group_field).to_have_value("QA Group")
    expect(detail.description_field).to_have_value("QA description text")
    expect(detail.reference_url_field).to_have_value("https://example.com/qa")


@pytest.mark.regression
def test_blank_common_fields_still_save(fields_page: FieldsPage):
    name = "Detail Blank Save"
    fields_page.create_field(name, "Text")

    detail = open_detail(fields_page, name)
    detail.save()

    expect(detail.banner).to_contain_text(f"Field {name} saved successfully.")


@pytest.mark.regression
def test_category_add_item_persists(fields_page: FieldsPage):
    name = "Detail Category Items"
    fields_page.create_field(name, "Category")

    detail = open_detail(fields_page, name)
    detail.add_item()
    detail.value_header_input(0).fill("High")
    detail.value_description_input(0).fill("High measurement value")
    detail.save()

    expect(detail.banner).to_contain_text(f"Field {name} saved successfully.")
    expect(detail.value_header_input(0)).to_have_value("High")
    expect(detail.value_description_input(0)).to_have_value("High measurement value")


@pytest.mark.regression
def test_category_add_multiple_items(fields_page: FieldsPage):
    name = "Detail Category Multi Items"
    fields_page.create_field(name, "Category")

    detail = open_detail(fields_page, name)
    detail.add_item()
    detail.value_header_input(0).fill("High")
    detail.value_description_input(0).fill("High value")
    detail.add_item()
    detail.value_header_input(1).fill("Low")
    detail.value_description_input(1).fill("Low value")
    detail.save()

    expect(detail.banner).to_contain_text(f"Field {name} saved successfully.")
    expect(detail.value_header_input(0)).to_have_value("High")
    expect(detail.value_header_input(1)).to_have_value("Low")


@pytest.mark.regression
def test_category_duplicate_values_blocks_save(fields_page: FieldsPage):
    name = "Detail Category Duplicates"
    fields_page.create_field(name, "Category")

    detail = open_detail(fields_page, name)
    detail.add_item()
    detail.value_header_input(0).fill("High")
    detail.add_item()
    detail.value_header_input(1).fill("High")
    detail.save()

    expect(detail.banner).to_contain_text("Duplicate values found: High")
    expect(detail.banner).to_contain_text("Please make them unique before saving")

    # Fixing the duplicate should let it save normally.
    detail.value_header_input(1).fill("Low")
    detail.save()

    expect(detail.banner).to_contain_text(f"Field {name} saved successfully.")


@pytest.mark.regression
def test_measurement_fields_persist(fields_page: FieldsPage):
    name = "Detail Measurement Fields"
    fields_page.create_field(name, "Measurement")

    detail = open_detail(fields_page, name)
    detail.trait_field.fill("Height")
    detail.unit_field.fill("cm")
    detail.method_field.fill("Ruler")
    detail.add_item()
    detail.parameter_input(0).fill("Precision")
    detail.value_input(0).fill("0.1")
    detail.save()

    expect(detail.banner).to_contain_text(f"Field {name} saved successfully.")
    expect(detail.trait_field).to_have_value("Height")
    expect(detail.unit_field).to_have_value("cm")
    expect(detail.method_field).to_have_value("Ruler")
    expect(detail.parameter_input(0)).to_have_value("Precision")
    expect(detail.value_input(0)).to_have_value("0.1")


@pytest.mark.regression
def test_detail_values_round_trip_after_navigation(fields_page: FieldsPage):
    name = "Detail Round Trip"
    fields_page.create_field(name, "Text")

    detail = open_detail(fields_page, name)
    detail.group_field.fill("Round Trip Group")
    detail.save()

    fields_page.page.get_by_role("link", name="Fields").click()
    detail = open_detail(fields_page, name)

    expect(detail.group_field).to_have_value("Round Trip Group")
