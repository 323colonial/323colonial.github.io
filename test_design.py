from pathlib import Path
import re


PAGES = ("index.html", "brochure.html", "floorplans.html", "sale-prep.html")
REQUIRED_TOKENS = (
    "--color-forest-ink",
    "--color-canopy-green",
    "--color-warm-paper",
    "--color-card-white",
    "--color-sage-rule",
    "--color-fieldstone-border",
    "--font-display",
    "--font-label",
    "--radius-none",
    "--space-section-gutter",
)
REQUIRED_COMPONENTS = (
    ".site-header",
    ".site-nav",
    ".media-card",
    ".swatch",
    ".data-table",
    ".information-band",
)


def main() -> None:
    stylesheet = Path("styles.css")
    assert stylesheet.exists(), "shared styles.css is missing"
    css = stylesheet.read_text()

    for token in REQUIRED_TOKENS:
        assert token in css, f"missing design token: {token}"
    for selector in REQUIRED_COMPONENTS:
        assert selector in css, f"missing component selector: {selector}"

    for page in PAGES:
        html = Path(page).read_text()
        assert '<meta name="viewport" content="width=device-width, initial-scale=1">' in html, f"{page}: viewport metadata missing"
        assert '<link rel="stylesheet" href="styles.css">' in html, f"{page}: shared stylesheet missing"
        assert not re.search(r"<style\b", html, re.I), f"{page}: embedded stylesheet remains"
        assert not re.search(r"\sstyle=", html, re.I), f"{page}: inline style remains"

    print(f"PASS: shared design system wired across {len(PAGES)} pages")


if __name__ == "__main__":
    main()
