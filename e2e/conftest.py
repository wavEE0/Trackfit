import os, pytest
from playwright.sync_api import Page

E2E_USER = "e2e_testuser"

@pytest.fixture(scope="session")
def base_url(request) -> str:
    cli = request.config.getoption("--base-url", default=None)
    return cli or os.environ.get("E2E_BASE_URL", "http://localhost:8000")

def _login(page: Page, base_url: str, username: str = E2E_USER) -> None:
    resp = page.request.get(f"{base_url}/e2e-login/?u={username}")
    assert resp.ok, f"Test login failed ({resp.status}). Run with DEBUG=True and seed_e2e."

@pytest.fixture
def authenticated_page(page: Page, base_url: str) -> Page:
    _login(page, base_url)
    return page
