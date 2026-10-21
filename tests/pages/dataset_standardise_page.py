from playwright.sync_api import Locator, Page

from tests.pages.base_page import BasePage, click_until, click_until_url_contains


class DatasetStandardisePage(BasePage):
    """The two-page /standardise/{id} wizard: map columns to Fields (page 1),
    then map Category column values (page 2)."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.next_button = page.get_by_role("button", name="Next", exact=True)
        self.back_button = page.get_by_role("button", name="Back", exact=True)
        self.finish_button = page.get_by_role("button", name="Finish", exact=True)
        # Success/info banners render with role="status"; danger/warning
        # banners (e.g. validation errors) render with role="alert" instead
        # of "status" - never both at once. Match either.
        self.banner = page.locator('[role="status"], [role="alert"]')

    def heading(self, name: str) -> Locator:
        return self.page.get_by_role("heading", name=f"Standardising Dataset: {name}")

    def type_dropdown(self, column_index: int) -> Locator:
        # rio.Dropdown has no accessibility_label in this Rio version, so
        # there's no per-column accessible name - position matches the
        # uploaded CSV's column order. Only valid when no Fields exist yet:
        # once they do, each column gets a second (existing-field) combobox -
        # use type_dropdown_with_existing_fields instead.
        return self.page.get_by_role("combobox").nth(column_index)

    def select_type(self, column_index: int, field_type: str) -> None:
        self._select_from_dropdown(self.type_dropdown(column_index), field_type)

    def existing_field_dropdown(self, column_index: int) -> Locator:
        # Only present once at least one Field exists - comboboxes then
        # interleave [existing-field dropdown, type dropdown] per column.
        return self.page.get_by_role("combobox").nth(column_index * 2)

    def type_dropdown_with_existing_fields(self, column_index: int) -> Locator:
        return self.page.get_by_role("combobox").nth(column_index * 2 + 1)

    def select_existing_field(self, column_index: int, field_label: str) -> None:
        self._select_from_dropdown(self.existing_field_dropdown(column_index), field_label)

    def select_type_with_existing_fields(self, column_index: int, field_type: str) -> None:
        self._select_from_dropdown(self.type_dropdown_with_existing_fields(column_index), field_type)

    def _select_from_dropdown(self, dropdown: Locator, option_name: str, attempts: int = 5) -> None:
        # exact=False: the "map to existing Field/value" options are labelled
        # f"{group} / {type} / {header}" with group empty for most test
        # fields, i.e. a leading space before the slash - match by substring
        # instead of guessing the exact leading whitespace.
        option = self.page.get_by_role("option", name=option_name, exact=False)
        for _ in range(attempts):
            # Right after a switcherbar toggle enables this dropdown, there's
            # a brief window where it's still effectively inert server-side -
            # clicking too early opens no menu at all, so retry the whole
            # open-and-select sequence rather than just the option click.
            dropdown.click(force=True)
            try:
                option.wait_for(state="visible", timeout=1000)
                option.click()
                option.wait_for(state="hidden", timeout=2000)
                return
            except Exception:
                pass
        raise TimeoutError(f"Could not select option {option_name!r} from dropdown")

    def switch_button(self, column_index: int, value: str) -> Locator:
        # Two listbox-role elements render per column - the second appears
        # to be a static duplicate with no pressed state; the first is the
        # real, interactive switcherbar.
        return (
            self.page.get_by_role("listbox")
            .nth(column_index * 2)
            .get_by_role("button", name=value, exact=True)
        )

    def select_existing_switch(self, column_index: int) -> None:
        self.switch_button(column_index, "Existing").click(force=True)

    def select_new_switch(self, column_index: int) -> None:
        self.switch_button(column_index, "New").click(force=True)

    def go_to_page_2(self) -> None:
        click_until(self.finish_button, self.next_button, "visible")

    def back_to_page_1(self) -> None:
        click_until(self.next_button, self.back_button, "visible")

    # --- Page 2: per-value mapping (same shape as page 1's per-column mapping,
    # scoped to one Category column's unique raw values instead) ---

    def existing_value_dropdown(self, value_index: int) -> Locator:
        # Unlike page 1's per-column pair (existing-field + type), each value
        # row has only ONE combobox (there's no "type" for a value) - so no
        # doubling here, just one per value in row order. The listbox switcher
        # pair still doubles per row, same as page 1.
        return self.page.get_by_role("combobox").nth(value_index)

    def select_existing_value(self, value_index: int, value_label: str) -> None:
        self._select_from_dropdown(self.existing_value_dropdown(value_index), value_label)

    def value_switch_button(self, value_index: int, value: str) -> Locator:
        # Filter to "Existing"/"New" listboxes specifically - a Date column's
        # ambiguous-format SwitcherBar (SSM-29) also renders as a listbox
        # ("Day first"/"Month first"), and would otherwise shift every
        # subsequent value_index if it appears earlier on the page.
        return (
            self.page.get_by_role("listbox").filter(has_text="Existing")
            .nth(value_index * 2)
            .get_by_role("button", name=value, exact=True)
        )

    def select_value_existing_switch(self, value_index: int) -> None:
        self.value_switch_button(value_index, "Existing").click(force=True)

    def select_value_new_switch(self, value_index: int) -> None:
        self.value_switch_button(value_index, "New").click(force=True)

    def new_value_input(self, raw_value: str) -> Locator:
        return self.page.get_by_role("textbox", name=f"New value for {raw_value}", exact=True)

    # --- Page 2: ambiguous/unreliable Date column handling (SSM-29) ---

    def date_order_switch_button(self, value: str) -> Locator:
        # The "Day first"/"Month first" SwitcherBar also renders as a
        # listbox, distinguished from the per-value Existing/New switchers by
        # its own text - only present at all when a mapped Date column's
        # format is ambiguous.
        return (
            self.page.get_by_role("listbox").filter(has_text="Day first")
            .first
            .get_by_role("button", name=value, exact=True)
        )

    def select_day_first(self) -> None:
        self.date_order_switch_button("Day first").click(force=True)

    def select_month_first(self) -> None:
        self.date_order_switch_button("Month first").click(force=True)

    def unreliable_date_error(self, header: str) -> Locator:
        return self.page.get_by_text(
            f"Error: {header} does not have a consistent, reliable date format", exact=False
        )

    def native_date_format_message(self) -> Locator:
        return self.page.get_by_text("Excel native date format detected", exact=False)

    def finish(self) -> None:
        # This triggers real server-side work (updating Fields, writing the
        # standardised CSV/XLSX to S3) before a success TextDialog appears,
        # which can take a few seconds - a longer per-attempt timeout than
        # click_until's default covers that wait.
        dialog = self.page.get_by_role("dialog")
        click_until(dialog, self.finish_button, "visible", attempts=3, timeout=6000)

        ok_button = self.page.get_by_text("Ok", exact=True)
        click_until_url_contains(self.page, ok_button, "/datasets", attempts=3)
        # The success dialog can take a moment to fully detach from the DOM
        # after the URL changes - give it time before the caller opens any
        # new dialog, to avoid a transient two-dialogs-at-once race.
        self.page.get_by_role("dialog").wait_for(state="hidden", timeout=5000)
