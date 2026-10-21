# Spreadsheet Schema Manager — Playwright Tests

End-to-end test suite for `spreadsheet-schema-manager-rio`, written with
[Playwright](https://playwright.dev/python/) and [pytest](https://docs.pytest.org/).

## Prerequisites

- Python 3.12+
- The app under test running with `AUTH_DISABLED=true` (this suite drives the app as an
  anonymous, ephemeral test user — see below)

## Install

```bash
pip install -r requirements.txt
playwright install chromium
```

## Running the tests

```bash
pytest                              # everything
pytest -m smoke                     # fast smoke subset
pytest -m regression                # full regression suite
pytest tests/e2e/test_fields.py     # a single file
```

By default, tests run against the UAT environment configured in `tests/conftest.py`'s
`base_url` fixture.

## Structure

- `tests/pages/` — Page Object Model wrappers around the app's pages (`FieldsPage`,
  `WorkbookDetailPage`, etc.)
- `tests/e2e/` — the actual test cases, grouped by feature area
- `tests/conftest.py` — shared fixtures (viewport sizes, browser context config)

## Important: session/user isolation

The app under test runs with `AUTH_DISABLED=true`, which attaches a fresh, isolated synthetic
user to every new browser session — not just every test, but every full page navigation. This
is intentional and gives every test its own clean "personal space" with zero cross-test data
leakage, but it means:

- Only call `.goto()` **once** per test (typically via a page object's `goto()` in a fixture).
- Any further in-test navigation between pages must go through the app's own nav-bar links
  (e.g. `page.get_by_role("link", name="Fields", exact=True).click()`), not another `.goto()` —
  otherwise the test lands in a brand-new session that can't see data it just created.

## CI

Tests run in Jenkins (see `Jenkinsfile`) against the Microsoft Playwright Docker image, triggered
from the app's own UAT deployment pipeline.

## Contributing

Contributions are welcome. If you are planning a change, please open an issue or discussion first
so the intended approach and scope are clear.

When updating tests, fixtures, or environment assumptions, also update the relevant README and test
documentation so the suite remains reliable and easy to operate.

## License

Licensed under the Apache License, Version 2.0 — see [LICENSE](LICENSE) and [NOTICE](NOTICE) for details.

## Funding

Funded by the New Zealand Ministry of Business, Innovation and Employment Strategic Science
Investment Fund (contract number C11X1702) as part of the Digital Horticulture Systems Ngā Pou
Rangahau, a Growing Futures™ programme at The New Zealand Institute for Bioeconomy Science
Limited (Bioeconomy Science Institute).
