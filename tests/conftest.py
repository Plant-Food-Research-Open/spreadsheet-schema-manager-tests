import os

import pytest
from dotenv import load_dotenv
from playwright.sync_api import Page

from tests.pages.datasets_page import DatasetsPage
from tests.pages.fields_page import FieldsPage
from tests.pages.workbooks_page import WorkbooksPage

load_dotenv()

# The app's UAT auth bypass attaches a fresh synthetic user to every new
# session (never looked up or reused across sessions - see auth.py's
# AUTH_DISABLED). Since pytest-playwright gives each test its own browser
# context/session, every test gets its own clean, isolated "personal
# space" for free: no cross-test data leakage, and no need to give
# created Fields/Templates/Workbooks unique names or clean them up
# between tests.


@pytest.fixture(scope="session")
def base_url():
    return os.getenv("BASE_URL", "https://spreadsheet-schema-manager.uat.k8s.pfr.co.nz")


@pytest.fixture(
    params=[
        {"width": 1920, "height": 1080},
    ],
    ids=["1920x1080"],
)
def viewport_size(request):
    return request.param


@pytest.fixture
def browser_context_args(browser_context_args, base_url, playwright, viewport_size):
    return {
        **browser_context_args,
        **playwright.devices["Desktop Chrome"],
        "base_url": base_url,
        "ignore_https_errors": True,
        "viewport": viewport_size,
    }


@pytest.fixture
def workbooks_page(page: Page) -> WorkbooksPage:
    return WorkbooksPage(page).goto()


@pytest.fixture
def fields_page(page: Page) -> FieldsPage:
    return FieldsPage(page).goto()


@pytest.fixture
def datasets_page(page: Page) -> DatasetsPage:
    return DatasetsPage(page).goto()

