import re, pytest
from playwright.sync_api import Page, expect

def test_homepage_loads(page: Page, base_url: str) -> None:
    page.goto(base_url + "/")
    expect(page).to_have_title(re.compile(r"Trackfit|TrackFit", re.IGNORECASE))

def test_homepage_body_visible(page: Page, base_url: str) -> None:
    page.goto(base_url + "/")
    expect(page.locator("body")).to_be_visible()
    assert "Server Error" not in page.content()

def test_dashboard_accessible_after_login(page: Page, base_url: str) -> None:
    resp = page.request.get(f"{base_url}/e2e-login/?u=e2e_testuser")
    if resp.status == 404:
        pytest.skip("e2e_testuser not found -- run: python manage.py seed_e2e")
    assert resp.ok, f"Login failed: {resp.status}"
    page.goto(base_url + "/dashboard")
    expect(page.locator("body")).to_be_visible()
    assert "Server Error" not in page.content()
