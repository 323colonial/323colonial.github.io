from pathlib import Path
import re


PAGES = ("index.html", "gallery.html")
REQUIRED_TOKENS = (
    "--forest",
    "--ink",
    "--paper",
    "--paper-strong",
    "--rule",
    "--muted",
    "--debonair",
    "--sea-salt",
    "--accessible-beige",
    "--greek-villa",
    "--mahogany",
)
REQUIRED_COMPONENTS = (
    ".masthead",
    ".header-contact",
    ".button",
    ".media-record",
    ".detail-grid",
    ".gallery-grid",
    ".viewer-controls",
)


def main() -> None:
    stylesheet = Path("listing.css")
    assert stylesheet.exists(), "shared listing.css is missing"
    css = stylesheet.read_text()

    for token in REQUIRED_TOKENS:
        assert token in css, f"missing design token: {token}"
    for selector in REQUIRED_COMPONENTS:
        assert selector in css, f"missing component selector: {selector}"

    assert "https://fonts.googleapis.com" not in css, "remote font dependency remains"
    assert re.search(r"button, \.button, summary, \.text-link \{[^}]*min-height: 44px", css), "buyer control targets are shorter than 44px"
    assert re.search(r"\.property-identity h1 a \{[^}]*min-height: 32px", css), "property home-link target is shorter than 32px"

    design = Path("DESIGN.md").read_text()
    assert "House-color property narrative" in design, "approved design direction is undocumented"
    assert "#593a32" in design, "shipped dark mahogany approximation is undocumented"
    assert re.search(r"\.masthead \{[^}]*background: var\(--mahogany\)", css), "masthead must use house dark mahogany"
    assert "--pewter-green" not in css, "historical door paint must not anchor current buyer palette"
    assert "The Woodland Survey" not in design, "superseded design direction remains"

    for page in PAGES:
        html = Path(page).read_text()
        assert '<meta name="viewport" content="width=device-width, initial-scale=1">' in html, f"{page}: viewport metadata missing"
        assert '<link rel="stylesheet" href="listing.css">' in html, f"{page}: stylesheet missing"
        assert not re.search(r"<style\b", html, re.I), f"{page}: embedded stylesheet remains"
        assert not re.search(r"\sstyle=", html, re.I), f"{page}: inline style remains"

    print(f"PASS: buyer styles wired across {len(PAGES)} pages")


if __name__ == "__main__":
    main()
