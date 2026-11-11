"""Walk through the docs tutorials on a deployed app and capture their screenshots.

The tutorials live in the app repo's docs (docs/source/tutorials/). This script
repeats their steps, in order, using the same sample data, and saves a
screenshot at each point a tutorial shows one. Rerun it whenever the UI
changes, then rebuild the docs.

- "Your first Workbook" and "Reuse a setup with Templates" run in one session,
  since the second continues from the first.
- "From legacy spreadsheets to a shared schema" runs in a fresh session, since
  it assumes no Fields to begin with.

Not part of the test suite: it lives outside tests/ so pytest never collects it.

Usage, from the root of this repo:

    python scripts/tutorial_screenshots.py \\
        --base-url https://<uat-host> \\
        --app-repo ../spreadsheet-schema-manager

The app must run with AUTH_DISABLED=true, so each session gets a fresh, empty
user. Screenshots are written to
<app-repo>/docs/source/_static/screenshots/<tutorial>/.
"""

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from playwright.sync_api import Browser, Page, Playwright, sync_playwright  # noqa: E402

from tests.pages.dataset_standardise_page import DatasetStandardisePage  # noqa: E402
from tests.pages.datasets_page import DatasetsPage, SheetSelectionDialog  # noqa: E402
from tests.pages.field_detail_page import FieldDetailPage  # noqa: E402
from tests.pages.fields_page import FieldsPage  # noqa: E402
from tests.pages.workbook_detail_page import TemplateDetailPage, WorkbookDetailPage  # noqa: E402
from tests.pages.workbook_download_page import WorkbookDownloadPage  # noqa: E402
from tests.pages.workbooks_page import TemplatesPage, WorkbooksPage  # noqa: E402

# Wide enough that the Datasets table doesn't scroll sideways.
VIEWPORT = {"width": 1600, "height": 900}


class Shooter:
    def __init__(self, page: Page, out_dir: Path):
        self.page = page
        self.out_dir = out_dir
        out_dir.mkdir(parents=True, exist_ok=True)

    def __call__(self, name: str) -> None:
        # Rio renders over a websocket after navigation settles; give it a moment.
        self.page.wait_for_timeout(1000)
        path = self.out_dir / f"{name}.png"
        self.page.screenshot(path=str(path), animations="disabled", timeout=60000)
        print("saved", path.relative_to(self.out_dir.parent))


def new_session(p: Playwright, browser: Browser, base_url: str) -> Page:
    context = browser.new_context(
        # Without a desktop browser profile, Rio treats headless Chromium as a
        # search-engine crawler.
        **{**p.devices["Desktop Chrome"], "viewport": VIEWPORT},
        base_url=base_url,
        ignore_https_errors=True,
    )
    return context.new_page()


def nav(page: Page, link: str) -> None:
    page.get_by_role("link", name=link, exact=True).click()
    page.wait_for_timeout(1000)


def retry_click_until_gone(page: Page, button_name: str) -> None:
    """Click a button that disappears once its action applies. A click landing
    mid-render can be dropped, so retry until it's gone."""
    button = page.get_by_role("button", name=button_name, exact=True)
    button.wait_for()
    for _ in range(5):
        button.click(force=True)
        page.wait_for_timeout(500)
        if button.count() == 0:
            return
    raise RuntimeError(f"{button_name!r} had no effect")


def tick_fields(page: Page, names: list[str]) -> None:
    """Tick the selection checkboxes of the named Fields on a Template/Workbook page.

    The table has no per-row DOM wrapper, so match each Field's row position via
    the order of its link in the table.
    """
    page.get_by_role("checkbox").first.wait_for()
    page.wait_for_timeout(500)
    nav_links = {"Datasets", "Workbooks", "Templates", "Fields", "Settings", "Logout"}
    field_links = [
        name for name in (link.inner_text().strip() for link in page.get_by_role("link").all())
        if name not in nav_links
    ]
    boxes = page.get_by_role("checkbox")
    for name in names:
        box = boxes.nth(field_links.index(name))
        for _ in range(5):
            if box.is_checked():
                break
            box.click(force=True)
            page.wait_for_timeout(300)
        else:
            raise RuntimeError(f"Could not tick {name!r}")


def set_field_order(page: Page, target: list[str]) -> WorkbookDownloadPage:
    download = WorkbookDownloadPage(page)
    for i, name in enumerate(target):
        while download.field_order().index(name) > i:
            download.move_field_up(name)
    assert download.field_order() == target, download.field_order()
    return download


def add_category_values(field: FieldDetailPage, values: list[tuple[str, str]], start: int = 0) -> None:
    if start:
        # add_item counts the existing rows: wait until they've rendered.
        field.delete_row_button(start).wait_for()
    for i, (value, desc) in enumerate(values, start=start):
        field.add_item()
        field.value_header_input(i).fill(value)
        field.value_description_input(i).fill(desc)


# --- Your first Workbook ---------------------------------------------------

def first_workbook(page: Page, shot: Shooter) -> None:
    fields = FieldsPage(page).goto()
    fields.heading.wait_for()

    dialog = fields.open_add_field_dialog()
    dialog.fill_name("Cultivar").select_type("Category")
    shot("new-field")
    dialog.save()
    FieldsPage(page).open_field("Cultivar")
    field = FieldDetailPage(page)
    add_category_values(field, [("Envy", ""), ("Gala", "")])
    shot("cultivar")
    field.save()

    nav(page, "Fields")
    FieldsPage(page).create_field("FruitHeight", "Category")
    FieldsPage(page).open_field("FruitHeight")
    field = FieldDetailPage(page)
    add_category_values(field, [("High", "Upper canopy"), ("Low", "Lower canopy")])
    field.save()

    nav(page, "Fields")
    FieldsPage(page).create_field("Weight", "Measurement")
    FieldsPage(page).open_field("Weight")
    field = FieldDetailPage(page)
    field.trait_field.fill("Weight of a fresh fruit")
    field.unit_field.fill("kg")
    field.method_field.fill("Weigher")
    shot("weight")
    field.save()

    for name, field_type in [("Rep", "Number"), ("HarvestDate", "Date")]:
        nav(page, "Fields")
        FieldsPage(page).create_field(name, field_type)
    nav(page, "Fields")
    shot("fields")

    nav(page, "Workbooks")
    WorkbooksPage(page).create("Fruit assessment 2026")
    WorkbooksPage(page).open_item("Fruit assessment 2026")
    workbook = WorkbookDetailPage(page)
    shot("workbook-new")
    tick_fields(page, ["Cultivar", "FruitHeight", "Weight", "Rep", "HarvestDate"])
    workbook.save()
    shot("workbook")

    workbook.go_to_download_page()
    set_field_order(page, ["Cultivar", "FruitHeight", "HarvestDate", "Rep", "Weight"])
    shot("download")
    # Leave the download page for the next tutorial.
    WorkbookDownloadPage(page).go_back()
    page.wait_for_timeout(1000)


# --- Reuse a setup with Templates --------------------------------------------

def templates(page: Page, shot: Shooter) -> None:
    # Continues on the "Fruit assessment 2026" Workbook page.
    workbook = WorkbookDetailPage(page)
    workbook.save_as_template("Fruit assessment")
    nav(page, "Templates")
    shot("templates")

    # The Fields change for next season.
    nav(page, "Fields")
    FieldsPage(page).open_field("Cultivar")
    field = FieldDetailPage(page)
    add_category_values(field, [("Jazz", "")], start=2)
    field.save()
    nav(page, "Fields")
    FieldsPage(page).create_field("Site", "Category")
    FieldsPage(page).open_field("Site")
    field = FieldDetailPage(page)
    add_category_values(field, [("Block A", "North block"), ("Block B", "South block")])
    shot("site")
    field.save()

    nav(page, "Templates")
    TemplatesPage(page).open_item("Fruit assessment")
    template = TemplateDetailPage(page)
    page.get_by_role("checkbox").first.wait_for()
    shot("template-before-update")
    template.update_fields()
    shot("template-after-update")
    tick_fields(page, ["Site"])
    template.save()

    nav(page, "Templates")
    dialog = TemplatesPage(page).create_workbook_from("Fruit assessment")
    dialog.fill_name("Fruit assessment 2027 Block A")
    dialog.save()
    nav(page, "Workbooks")
    WorkbooksPage(page).open_item("Fruit assessment 2027 Block A")
    workbook = WorkbookDetailPage(page)
    retry_click_until_gone(page, "Remove Block B")
    workbook.save()
    shot("workbook")


# --- From legacy spreadsheets to a shared schema -----------------------------

def legacy_chapter_1(page: Page, shot: Shooter, data: Path) -> None:
    datasets = DatasetsPage(page).goto()
    datasets.heading.wait_for()
    datasets.upload(str(data / "Dataset1.csv"))
    shot("01-dataset1-warning")
    datasets.go_to_raw_view("Dataset1")
    shot("01-raw-data-view")
    page.go_back()
    datasets = DatasetsPage(page)
    datasets.heading.wait_for()
    datasets.upload(str(data / "Dataset1_fixed.csv"))
    datasets.delete("Dataset1").confirm()
    shot("01-dataset1-fixed")


def legacy_chapter_2(page: Page, shot: Shooter) -> None:
    DatasetsPage(page).go_to_standardise_wizard("Dataset1_fixed")
    std = DatasetStandardisePage(page)
    std.select_type(3, "Number")  # FruitNumber: detected as Measurement
    shot("02-columns")
    std.go_to_page_2()
    shot("02-values")
    std.finish()
    nav(page, "Fields")
    shot("02-fields")


def legacy_chapter_3(page: Page, shot: Shooter, data: Path) -> None:
    nav(page, "Datasets")
    datasets = DatasetsPage(page)
    dialog = datasets.open_upload_dialog()
    dialog.choose_file(str(data / "Dataset2.xlsx"))
    dialog.save()
    sheet = SheetSelectionDialog(page)
    sheet.dialog.wait_for()
    shot("03-select-sheet")
    sheet.select_sheet("RawData").confirm()
    datasets.go_to_standardise_wizard("Dataset2_RawData")
    std = DatasetStandardisePage(page)
    shot("03-columns-defaults")
    std.select_existing_field(3, "FruitHeight")  # Height: guessed as Weight
    std.select_type_with_existing_fields(4, "Number")  # Rep: detected as Measurement
    shot("03-columns-corrected")
    std.go_to_page_2()
    shot("03-values")
    std.finish()


def legacy_chapter_4(page: Page, shot: Shooter) -> None:
    nav(page, "Fields")
    shot("04-fields-before")
    FieldsPage(page).open_field("FruitHeight")
    field = FieldDetailPage(page)
    field.delete_first_value_row()  # H
    field.delete_first_value_row()  # L
    shot("04-fruitheight")
    field.save()
    nav(page, "Fields")
    FieldsPage(page).delete_field("FruitNumber").confirm()
    FieldsPage(page).delete_field("Date").confirm()
    for name, trait, unit, method in [
        ("Diameter", "Diameter of a fresh fruit", "cm", "Ruler"),
        ("Weight", "Weight of a fresh fruit", "kg", "Weigher"),
    ]:
        nav(page, "Fields")
        FieldsPage(page).open_field(name)
        field = FieldDetailPage(page)
        field.trait_field.fill(trait)
        field.unit_field.fill(unit)
        field.method_field.fill(method)
        if name == "Weight":
            shot("04-weight")
        field.save()
    nav(page, "Fields")
    shot("04-fields-final")


def legacy_chapter_5(page: Page, shot: Shooter) -> None:
    nav(page, "Datasets")
    DatasetsPage(page).go_to_standardise_wizard("Dataset1_fixed")
    std = DatasetStandardisePage(page)
    shot("05-dataset1-columns-defaults")
    std.select_existing_field(0, "HarvestDate")  # Date: guessed as Diameter
    std.select_existing_switch(3)  # FruitNumber: its old Field is gone
    std.select_existing_field(3, "Rep")
    shot("05-dataset1-columns")
    std.go_to_page_2()
    std.select_value_existing_switch(2)  # H
    std.select_existing_value(2, "High")
    std.select_value_existing_switch(3)  # L
    std.select_existing_value(3, "Low")
    shot("05-dataset1-values")
    std.finish()
    DatasetsPage(page).go_to_standardise_wizard("Dataset2_RawData")
    std = DatasetStandardisePage(page)
    std.select_existing_field(3, "FruitHeight")
    std.go_to_page_2()
    std.finish()
    shot("05-datasets-complete")


def legacy_chapter_6(page: Page, shot: Shooter, download_dir: Path | None) -> None:
    nav(page, "Fields")
    FieldsPage(page).create_field("Site", "Category")
    FieldsPage(page).open_field("Site")
    field = FieldDetailPage(page)
    add_category_values(field, [("Block A", "North block"), ("Block B", "South block")])
    field.save()

    nav(page, "Templates")
    TemplatesPage(page).create("Fruit assessment")
    TemplatesPage(page).open_item("Fruit assessment")
    tick_fields(page, ["Cultivar", "FruitHeight", "Site", "Diameter", "Weight", "Rep",
                       "AssessmentDate", "HarvestDate"])
    TemplateDetailPage(page).save()

    nav(page, "Templates")
    dialog = TemplatesPage(page).create_workbook_from("Fruit assessment")
    dialog.fill_name("Fruit assessment 2027")
    dialog.save()
    nav(page, "Workbooks")
    WorkbooksPage(page).open_item("Fruit assessment 2027")
    workbook = WorkbookDetailPage(page)
    retry_click_until_gone(page, "Remove Block B")
    workbook.save()
    shot("06-workbook")
    workbook.go_to_download_page()
    download = set_field_order(page, ["Site", "Cultivar", "FruitHeight", "HarvestDate",
                                      "AssessmentDate", "Rep", "Diameter", "Weight"])
    if download_dir:
        download.download().save_as(str(download_dir / "Fruit assessment 2027.xlsx"))
        download.go_back()
        page.wait_for_timeout(1000)
        qr = WorkbookDetailPage(page).download_qr()
        qr.save_as(str(download_dir / qr.suggested_filename))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--base-url", required=True, help="URL of the app, running with AUTH_DISABLED=true")
    parser.add_argument("--app-repo", type=Path, default=REPO_ROOT.parent / "spreadsheet-schema-manager")
    parser.add_argument("--download-dir", type=Path, help="Also save the advanced tutorial's downloads here, to check them")
    parser.add_argument("--only", choices=["basics", "legacy"], help="Run only one session")
    args = parser.parse_args()

    data = args.app_repo / "docs/source/_static/tutorial-data"
    shots = args.app_repo / "docs/source/_static/screenshots"
    if not data.is_dir():
        sys.exit(f"Tutorial data not found: {data}")

    with sync_playwright() as p:
        browser = p.chromium.launch()
        if args.only in (None, "basics"):
            page = new_session(p, browser, args.base_url)
            first_workbook(page, Shooter(page, shots / "first-workbook"))
            templates(page, Shooter(page, shots / "templates"))
            page.context.close()
        if args.only in (None, "legacy"):
            page = new_session(p, browser, args.base_url)
            shot = Shooter(page, shots / "legacy")
            legacy_chapter_1(page, shot, data)
            legacy_chapter_2(page, shot)
            legacy_chapter_3(page, shot, data)
            legacy_chapter_4(page, shot)
            legacy_chapter_5(page, shot)
            legacy_chapter_6(page, shot, args.download_dir)
            page.context.close()
        browser.close()


if __name__ == "__main__":
    main()
