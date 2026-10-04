"""Approved colonial-5bv copy, gallery, asset and preservation contract. No dependencies."""
import hashlib
import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import unittest

ROOT = Path(__file__).resolve().parents[1]
APPROVED = json.loads((ROOT / 'tests/fixtures/approved-listing.json').read_text())


class Element:
    def __init__(self, tag='', attrs=(), parent=None):
        self.tag, self.attrs, self.parent = tag, dict(attrs), parent
        self.children = []

    def all(self, tag):
        return [child for child in self.children if isinstance(child, Element)
                for child in ([child] if child.tag == tag else []) + child.all(tag)]

    def text(self):
        return ''.join(c.text() if isinstance(c, Element) else c for c in self.children)

    def cls(self, name):
        return name in self.attrs.get('class', '').split()


class Page(HTMLParser):
    def __init__(self, filename):
        super().__init__(convert_charrefs=True)
        self.root = self.current = Element()
        self.feed((ROOT / filename).read_text())

    def handle_starttag(self, tag, attrs):
        child = Element(tag, attrs, self.current)
        self.current.children.append(child)
        if tag not in {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'source', 'wbr'}:
            self.current = child

    def handle_endtag(self, tag):
        node = self.current
        while node.parent:
            if node.tag == tag:
                self.current = node.parent
                break
            node = node.parent

    def handle_data(self, text):
        self.current.children.append(text)


class Listing(unittest.TestCase):
    def test_exact_seven_paragraphs_and_inline_images(self):
        page = Page('index.html').root
        copy = [p for p in page.all('p') if p.cls('listing-copy')]
        self.assertEqual([p.text() for p in copy], APPROVED['paragraphs'])
        for paragraph in copy:
            self.assertTrue(paragraph.parent.parent.all('figure'), 'Each passage keeps matching inline imagery')
        hot_tub = next(f for f in page.all('figure') if any('06-small.webp' in i.attrs.get('src', '') for i in f.all('img')))
        self.assertIn('Placeholder photo — not this property', hot_tub.text())
        self.assertNotIn('Olympic Hot Tub', hot_tub.text())
        hero = next(img for img in page.all('img') if img.attrs.get('fetchpriority') == 'high')
        self.assertEqual(hero.attrs['src'], 'assets/listing/01.webp')

    def test_gallery_order_captions_and_disclosures(self):
        page = Page('gallery.html').root
        figures = [f for f in page.all('figure') if 'data-position' in f.attrs]
        self.assertEqual(len(figures), 33)
        for figure, expected in zip(figures, APPROVED['photos']):
            n = expected['position']
            self.assertEqual(int(figure.attrs['data-position']), n)
            caption = next(s for s in figure.all('span') if s.cls('caption-text'))
            self.assertEqual(caption.text(), expected['caption'])
            link = figure.all('a')[0]
            self.assertEqual(link.attrs['href'], f'assets/listing/{n:02}.webp')
            self.assertTrue(link.attrs.get('aria-label'))
            self.assertEqual(figure.all('img')[0].attrs['src'], f'assets/listing/{n:02}-small.webp')
            if n == 6:
                self.assertIn('Placeholder photo — not this property', figure.text())
                self.assertNotIn('Olympic Hot Tub', figure.text())
                self.assertNotIn('simulated', figure.text().lower())
            elif n == 31:
                self.assertIn('Conceptual basement plan', figure.text())
                self.assertIn('not existing finished space', figure.text())
            else:
                self.assertFalse(any(s.cls('photo-note') for s in figure.all('span')), 'Routine photo disclaimers removed')
        self.assertEqual(len(page.all('dialog')), 1)
        self.assertEqual(page.all('dialog')[0].attrs.get('aria-labelledby'), 'viewer-title')

    def test_public_navigation_and_listing_snapshot(self):
        for file in ('index.html', 'gallery.html'):
            page = Page(file).root
            nav = next(n for n in page.all('nav') if n.attrs.get('aria-label') == 'Buyer navigation')
            self.assertEqual([a.text() for a in nav.all('a')], ['Home', 'Photos'])
            self.assertEqual([a.attrs['href'] for a in nav.all('a')], ['index.html', 'gallery.html'])
            current = [a for a in nav.all('a') if 'aria-current' in a.attrs]
            self.assertEqual([(a.attrs['href'], a.attrs['aria-current']) for a in current], [(file, 'page')])
            siblings = [e for e in nav.parent.children if isinstance(e, Element)]
            self.assertEqual(nav.parent.tag, 'body')
            self.assertEqual(siblings[siblings.index(nav) - 1].tag, 'header')
            self.assertEqual(siblings[siblings.index(nav) + 1].tag, 'main')
            self.assertIn('tel:3048857645', [a.attrs.get('href') for a in page.all('a')])
            self.assertIn('https://www.redfin.com/WV/Berkeley-Springs/323-Colonial-Dr-25411/home/21971085', [a.attrs.get('href') for a in page.all('a')])
            self.assertIn('Liz McDonald', page.text())
            self.assertIn('Dandridge Realty Group LLC', page.text())
            self.assertNotRegex((ROOT / file).read_text(), r'floorplans\.html|brochure\.html|sale-prep\.html|mailto:|brightmls\.com|plan-main|plan-second|paint-colors')
        text = Page('index.html').root.text()
        for fact in ['$499,000', '2,081', 'above-grade', '2.90', '2008', 'Coming Soon', 'October 3, 2026', 'October 8, 2026', 'WVMO2008198', '2 full', '1 half']:
            self.assertIn(fact, text)

    def test_only_essential_disclosures_remain(self):
        for filename in ('index.html', 'gallery.html'):
            page = Page(filename).root
            text = page.text()
            for removed in ['watermark retained', 'Owner photograph', 'Prior-listing photograph',
                            'Listing photograph', 'snapshot', 'Status does not update',
                            'confirm availability', 'may differ', 'not a live feed',
                            'not a direct agent line', 'Not field-measured']:
                self.assertNotIn(removed, text, filename)
            self.assertEqual(text.count('October 3, 2026'), 1, 'Only footer carries listing date')
            self.assertIn('Listing information as of October 3, 2026.', text)
            notes = [s.text() for s in page.all('span') if s.cls('photo-note')]
            expected = ['Placeholder photo — not this property.']
            if filename == 'gallery.html':
                expected.append('Conceptual basement plan — not existing finished space.')
            self.assertEqual(notes, expected)

    def test_local_links_images_and_fragment_targets_resolve(self):
        for file in ('index.html', 'gallery.html'):
            page = Page(file).root
            for tag, attr in [('a', 'href'), ('img', 'src'), ('link', 'href'), ('script', 'src')]:
                for element in page.all(tag):
                    value = element.attrs.get(attr, '')
                    url = urlsplit(value)
                    if url.scheme or url.netloc:
                        continue
                    target = unquote(url.path) or file
                    self.assertTrue((ROOT / target).is_file(), f'{file}: {value}')
                    if url.fragment:
                        ids = {e.attrs['id'] for t in ['main', 'section', 'figure', 'h1', 'h2']
                               for e in Page(target).root.all(t) if 'id' in e.attrs}
                        self.assertIn(url.fragment, ids, value)
            for img in page.all('img'):
                self.assertTrue(img.attrs.get('alt'))
                self.assertGreater(int(img.attrs.get('width', 0)), 0)
                self.assertGreater(int(img.attrs.get('height', 0)), 0)
                for src in img.attrs.get('srcset', '').split(','):
                    if src.strip():
                        self.assertTrue((ROOT / src.split()[0]).is_file())

    def test_source_provenance_optimized_derivatives_and_legacy_preserved(self):
        manifest = ROOT / 'assets/listing/manifest.json'
        self.assertTrue(manifest.exists(), 'listing provenance manifest missing')
        data = json.loads(manifest.read_text())
        self.assertEqual(data['document_sha256'], APPROVED['document_sha256'])
        self.assertEqual(len(data['photos']), 33)
        for actual, expected in zip(data['photos'], APPROVED['photos']):
            for key in ['position', 'id', 'caption', 'source', 'source_sha256']:
                self.assertEqual(actual[key], expected[key])
            for derivative in actual['derivatives']:
                content = (ROOT / derivative['path']).read_bytes()
                self.assertEqual(hashlib.sha256(content).hexdigest(), derivative['sha256'])
                self.assertLess(len(content), 500_000)
                self.assertEqual(content[8:12], b'WEBP')
        for filename, expected in APPROVED['preserved_sha256'].items():
            self.assertEqual(hashlib.sha256((ROOT / filename).read_bytes()).hexdigest(), expected, filename)


if __name__ == '__main__':
    unittest.main()
