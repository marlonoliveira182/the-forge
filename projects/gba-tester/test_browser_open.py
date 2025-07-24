def test_browser_opens(page):
    page.goto("https://www.example.com")
    assert page.title() == "Example Domain" 