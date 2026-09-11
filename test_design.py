from pathlib import Path
import re


PAGES = ("index.html", "gallery.html", "brochure.html", "floorplans.html", "sale-prep.html")
REQUIRED_TOKENS = (
    "--forest",
    "--forest-ink",
    "--paper",
    "--paper-strong",
    "--rule",
    "--muted",
    "--white",
    "--font-display",
    "--font-serif",
    "--font-label",
)
REQUIRED_COMPONENTS = (
    ".listing-header",
    ".buyer-nav",
    ".button",
    ".media-record",
    ".swatch",
    ".data-table",
    ".showing-band",
)


def main() -> None:
    stylesheet = Path("styles.css")
    assert stylesheet.exists(), "shared styles.css is missing"
    css = stylesheet.read_text()

    for token in REQUIRED_TOKENS:
        assert token in css, f"missing design token: {token}"
    for selector in REQUIRED_COMPONENTS:
        assert selector in css, f"missing component selector: {selector}"

    assert "https://fonts.googleapis.com" not in css, "remote font dependency remains"
    assert re.search(r"@media \(max-width: 640px\)[\s\S]*?\.listing-header > \.button \{[^}]*min-height: 44px", css), "mobile showing CTA is shorter than 44px"
    assert re.search(r"\.property-mark \{[^}]*min-height: 44px", css), "property mark target is shorter than 44px"
    assert re.search(r"\.text-link \{[^}]*min-height: 44px", css), "isolated text-link target is shorter than 44px"
    assert re.search(r"\.planning-link \{[^}]*min-height: 44px", css), "hero planning-link target is shorter than 44px"
    assert not re.search(r"@media \(max-width: 640px\)[\s\S]*?\.data-table \{[^}]*min-width: 640px", css), "mobile tables still force horizontal scrolling"

    design = Path("DESIGN.md").read_text()
    assert "Mountain House Monograph" in design, "approved design direction is undocumented"
    assert "#183828" in design, "shipped forest token is undocumented"
    assert "The Woodland Survey" not in design, "superseded design direction remains"

    for page in PAGES:
        html = Path(page).read_text()
        assert '<meta name="viewport" content="width=device-width, initial-scale=1">' in html, f"{page}: viewport metadata missing"
        assert '<link rel="stylesheet" href="styles.css">' in html, f"{page}: shared stylesheet missing"
        assert not re.search(r"<style\b", html, re.I), f"{page}: embedded stylesheet remains"
        assert not re.search(r"\sstyle=", html, re.I), f"{page}: inline style remains"

    print(f"PASS: Mountain House Monograph system wired across {len(PAGES)} pages")


if __name__ == "__main__":
    main()
