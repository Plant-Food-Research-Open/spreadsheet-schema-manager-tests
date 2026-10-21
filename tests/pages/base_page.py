from playwright.sync_api import Locator, Page


def _in_state(locator: Locator, state: str) -> bool:
    if state == "visible":
        return locator.is_visible()
    if state == "hidden":
        return locator.is_hidden()
    raise ValueError(f"Unsupported state: {state!r}")


def click_until(locator: Locator, button: Locator, state: str, attempts: int = 5, timeout: int = 1000) -> None:
    """Force-click button and wait for locator to reach state.

    Rio's dropdown-close animation briefly overlaps buttons, intercepting
    the first click attempt, so this retries with a forced click. After a
    failed wait, an instant, non-waiting check decides whether to retry:
    if the state was actually reached just after the wait timed out, a
    wrongful re-click would be wrong - for a toggle-style button, it would
    flip the state straight back - so only click again if it's confirmed
    we're still not there. Raise timeout for actions with real server-side
    work between the click and the expected state (e.g. saving to S3).
    """
    for _ in range(attempts):
        button.click(force=True)
        try:
            locator.wait_for(state=state, timeout=timeout)
            return
        except Exception:
            pass
        if _in_state(locator, state):
            return
    raise TimeoutError(f"Locator did not reach state '{state}' after clicking button")


def click_until_closed(dialog: Locator, button: Locator, attempts: int = 5, timeout: int = 1000) -> None:
    click_until(dialog, button, "hidden", attempts, timeout)


def click_until_open(dialog: Locator, button: Locator, attempts: int = 5, timeout: int = 1000) -> None:
    click_until(dialog, button, "visible", attempts, timeout)


def click_until_download(page: Page, button: Locator, attempts: int = 5, per_attempt_timeout: int = 8000):
    """Force-click button, retrying the whole click+await-download cycle like click_until."""
    last_exc = None
    for _ in range(attempts):
        try:
            with page.expect_download(timeout=per_attempt_timeout) as download_info:
                button.click(force=True)
            return download_info.value
        except Exception as exc:
            last_exc = exc
    raise last_exc


def pressable(button: Locator) -> Locator:
    """The actual interactive DOM node inside a comps.Button/rio.Button.

    get_by_role("button", ...) resolves to the outer wrapper div, but Rio
    puts the real `aria-disabled` state on an inner <rio-pressable-element>
    - Playwright's to_be_disabled()/is_disabled() only look at the element
    itself, so checking the outer wrapper always reports "enabled". Chain
    this on to check the real disabled state, e.g.:
    expect(pressable(my_button)).to_have_attribute("aria-disabled", "true")
    """
    return button.locator("rio-pressable-element")


def click_until_url_contains(page: Page, button: Locator, fragment: str, attempts: int = 5, timeout: int = 1000) -> None:
    """Force-click button and wait for the URL to contain fragment, retrying like click_until."""
    for _ in range(attempts):
        button.click(force=True)
        try:
            page.wait_for_url(f"**{fragment}**", timeout=timeout)
            return
        except Exception:
            pass
        if fragment in page.url:
            return
    raise TimeoutError(f"URL did not come to contain {fragment!r} after clicking button")


class TypeFilterMixin:
    """Shared Group/Type filter menu behavior for pages using table_filter.py's FilterRow.

    Requires the consuming class to set self.page and self.type_filter_button.
    """

    def type_filter_option(self, field_type: str) -> Locator:
        # Rio renders the count in the accessible name, e.g. "Text (3)".
        return self.page.get_by_role("button", name=f"{field_type} (", exact=False)

    def toggle_type_filter(self, field_type: str) -> None:
        # Selecting an option never closes this menu - it's a multi-select
        # checkbox list, and only the filter button itself toggles it open
        # or closed. The selection takes effect immediately on click; the
        # caller can assert on its effect directly.
        menu = self.page.get_by_role("menu")
        click_until(menu, self.type_filter_button, "visible")
        self.type_filter_option(field_type).click(force=True)


class ConfirmDialog:
    """The Yes/No confirmation dialog used by row Delete and Delete All."""

    def __init__(self, page: Page):
        self.page = page
        self.dialog = page.get_by_role("dialog")

    def confirm(self) -> None:
        click_until_closed(self.dialog, self.dialog.get_by_text("Yes", exact=True))

    def dismiss(self) -> None:
        click_until_closed(self.dialog, self.dialog.get_by_text("No", exact=True))


class BasePage:
    path = "/"

    def __init__(self, page: Page):
        self.page = page

    def goto(self):
        self.page.goto(self.path)
        return self

    def title(self) -> str:
        return self.page.title()
