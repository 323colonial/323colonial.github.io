"""Approved listing copy, gallery, asset and preservation contract. No dependencies."""
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
        self.assertEqual(hot_tub.text(), APPROVED['photos'][5]['caption'])
        hero = next(img for img in page.all('img') if img.attrs.get('fetchpriority') == 'high')
        self.assertEqual(hero.attrs['src'], 'assets/listing/01.webp')

    def test_narrative_photo_coverage_and_popouts(self):
        page = Page('index.html').root
        self.assertEqual([h.text() for h in page.all('h1')], ['323 Colonial Dr'])
        self.assertFalse(page.all('h3'))
        self.assertNotIn('About the home', page.text())
        self.assertNotIn('A closer look', page.text())
        stories = [s for s in page.all('section') if s.cls('story')]
        self.assertEqual(len(stories), 7)
        covered = {1}
        for story in stories:
            covered.update(int(a.attrs['data-photo']) for a in story.all('a') if 'data-photo' in a.attrs)
        self.assertEqual(covered, set(range(1, 34)), 'Every photo has a narrative home')
        plan = next(a for a in page.all('a') if a.attrs.get('data-photo') == '31')
        self.assertIn('additional finished living space', plan.text())
        self.assertIn('conceptual', plan.attrs['aria-label'].lower())
        self.assertIn(plan.text(), plan.attrs['aria-label'], 'Speech input can target the visible link wording')
        self.assertEqual({d.attrs['id'] for d in page.all('dialog')}, {'all-photos', 'photo-viewer', 'property-details'})

    def test_property_details_text_links_from_facts_heading(self):
        page = Page('index.html').root
        summary = next(s for s in page.all('section') if s.cls('listing-summary'))
        self.assertEqual(len(summary.all('h2')), 1, 'Facts bar needs property details heading')
        heading = summary.all('h2')[0]
        self.assertIn('Property details', heading.text())
        link = heading.all('a')[0]
        self.assertEqual(link.text(), 'Property details')
        self.assertEqual(link.attrs.get('aria-label', link.text()), 'Property details')
        self.assertFalse(any('$499,000' in a.text() for a in page.all('a')), 'Price is not linked')
        self.assertIn('$499,000', heading.text())
        self.assertEqual(link.attrs['href'], '#details', 'Native anchor fallback preserved')
        self.assertEqual(page.all('h2')[0], heading)

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
            if n == 31:
                self.assertIn('Conceptual basement plan', figure.text())
                self.assertIn('not existing finished space', figure.text())
            else:
                self.assertFalse(any(s.cls('photo-note') for s in figure.all('span')), 'Routine photo disclaimers removed')
        self.assertEqual(len(page.all('dialog')), 1)
        self.assertEqual(page.all('dialog')[0].attrs.get('aria-labelledby'), 'viewer-title')

    def test_public_navigation_and_listing_snapshot(self):
        for file in ('index.html', 'gallery.html'):
            page = Page(file).root
            self.assertFalse(page.all('nav'), 'Redundant Home / Photos navigation removed')
            header = page.all('header')[0]
            self.assertIn('323 Colonial Dr', header.text())
            self.assertIn('Berkeley Springs, WV 25411', header.text())
            self.assertIn('Liz McDonald', header.text())
            self.assertIn('Dandridge Realty Group LLC', header.text())
            self.assertIn('tel:+13048851547', [a.attrs.get('href') for a in page.all('a')])
            self.assertIn('https://www.redfin.com/WV/Berkeley-Springs/323-Colonial-Dr-25411/home/21971085', [a.attrs.get('href') for a in page.all('a')])
            self.assertIn('Liz McDonald', page.text())
            self.assertIn('Dandridge Realty Group LLC', page.text())
            self.assertNotRegex((ROOT / file).read_text(), r'floorplans\.html|brochure\.html|sale-prep\.html|brightmls\.com|plan-main|plan-second|paint-colors')
        text = Page('index.html').root.text()
        for fact in ['$499,000', '2,081', '2.90', '2008', 'Coming Soon', 'October 3, 2026', 'October 8, 2026', 'WVMO2008198', '2 full', '1 half']:
            self.assertIn(fact, text)

    def test_square_footage_without_grade_qualifier(self):
        page = Page('index.html').root
        facts = next(p for p in page.all('p') if p.cls('quick-facts'))
        self.assertEqual([s.text() for s in facts.all('span')][2], '2,081 sq ft')
        details = next(dl for dl in page.all('dl') if dl.cls('detail-grid'))
        values = dict(zip((dt.text() for dt in details.all('dt')),
                          (dd.text() for dd in details.all('dd'))))
        self.assertEqual(values['Finished area'], '2,081 sq ft')
        self.assertEqual(values['Lower level'], 'Unfinished walkout basement')
        self.assertNotRegex(page.text().lower(), r'above[\s-]+grade')

    def test_title_page_realtor_details_in_disclosure_and_print_footer_only(self):
        page = Page('index.html').root
        contact = next(d for d in page.all('details') if d.cls('showing-contact'))
        printed = [p for p in page.all('p') if p.cls('print-contact')]
        self.assertEqual(len(printed), 1)
        self.assertEqual(printed[0].parent.tag, 'footer')
        self.assertEqual(contact.all('summary')[0].text(), 'See in person')
        for detail in ('Liz McDonald', 'Listing agent', 'Dandridge Realty Group LLC'):
            self.assertEqual(contact.text().count(detail), 1)
            self.assertEqual(printed[0].text().count(detail), 1)
            self.assertEqual(page.text().count(detail), 2, f'{detail} repeated outside disclosure/print footer')
        self.assertEqual([a.attrs['href'] for a in contact.all('a')], [
            'tel:+13048851547',
            'mailto:liz@dandridgerealtygroup.com',
            'https://www.redfin.com/WV/Berkeley-Springs/323-Colonial-Dr-25411/home/21971085',
        ])

    def test_website_brokerage_contacts(self):
        for filename in ('index.html', 'gallery.html'):
            page = Page(filename).root
            contact = next(d for d in page.all('details') if d.cls('showing-contact'))
            links = contact.all('a')
            self.assertEqual(links[0].attrs['href'], 'tel:+13048851547')
            self.assertEqual(links[0].text(), 'Call brokerage · (304) 885-1547')
            self.assertEqual(links[1].attrs['href'], 'mailto:liz@dandridgerealtygroup.com')
            self.assertEqual(links[1].text(), 'Email Liz')
            self.assertNotRegex(page.text().lower(), r'michelle|283-8640|885-7645|fast response')
        printed = next(p for p in Page('index.html').root.all('p') if p.cls('print-contact'))
        self.assertIn('(304) 885-1547', printed.text())
        self.assertEqual(printed.all('a')[0].attrs['href'], 'tel:+13048851547')

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
            expected = ['Conceptual basement plan — not existing finished space.']
            self.assertEqual(notes, expected)

    def test_real_hot_tub_and_greenhouse_names(self):
        for filename in ('index.html', 'gallery.html'):
            page = Page(filename).root
            self.assertNotIn('placeholder', (ROOT / filename).read_text().lower())
            for position in (6, 25):
                figure = next(f for f in page.all('figure') if any(
                    i.attrs.get('src') == f'assets/listing/{position:02}-small.webp' for i in f.all('img')))
                self.assertEqual(figure.all('img')[0].attrs['alt'], APPROVED['photos'][position - 1]['caption'])
                self.assertFalse(any(s.cls('photo-note') for s in figure.all('span')))
                if position == 6:
                    image = figure.all('img')[0]
                    self.assertEqual((image.attrs['width'], image.attrs['height']), ('720', '542'))
                    self.assertIn('assets/listing/06.webp 1600w', image.attrs['srcset'])

    def test_local_links_images_and_fragment_targets_resolve(self):
        for file in ('index.html', 'gallery.html'):
            page = Page(file).root
            for tag, attr in [('a', 'href'), ('img', 'src'), ('link', 'href'), ('script', 'src')]:
                for element in page.all(tag):
                    value = element.attrs.get(attr, '')
                    url = urlsplit(value)
                    if url.scheme or url.netloc:
                        continue
                    target = 'index.html' if url.path == '/' else unquote(url.path).lstrip('/') or file
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

    def test_reviewed_margin_trims_and_responsive_dimensions(self):
        # Left, top, right, bottom: visually approved margins, not an auto-trim.
        margins = {
            10: (4, 9, 6, 5), 11: (8, 7, 12, 13), 12: (8, 10, 8, 12),
            13: (0, 10, 9, 8), 15: (8, 9, 10, 9), 17: (3, 5, 8, 5),
            18: (3, 7, 8, 6), 19: (6, 6, 4, 7), 21: (6, 12, 10, 6),
            22: (3, 10, 4, 4), 24: (6, 12, 6, 4), 26: (4, 6, 6, 6),
            28: (9, 8, 7, 6), 29: (8, 9, 6, 7), 32: (4, 9, 8, 9),
            33: (4, 5, 6, 5),
        }
        photos = json.loads((ROOT / 'assets/listing/manifest.json').read_text())['photos']
        dimensions = {}
        for photo in photos:
            full = photo['derivatives'][0]
            for d in photo['derivatives']:
                dimensions[d['path']] = (d['width'], d['height'])
                trim = d.get('margin_trim')
                if photo['position'] not in margins:
                    self.assertIsNone(trim)
                    continue
                self.assertIsNotNone(trim, f"Photo {photo['position']} still has its reviewed border")
                fw, fh = full['margin_trim']['input_size']
                iw, ih = trim['input_size']
                left, top, right, bottom = margins[photo['position']]
                left, right = left * iw // fw, right * iw // fw
                top, bottom = top * ih // fh, bottom * ih // fh
                self.assertEqual(trim['xywh'], [left, top, iw - left - right, ih - top - bottom])
                self.assertEqual((d['width'], d['height']), tuple(trim['xywh'][2:]))
                self.assertRegex(trim['retained_rgb_sha256'], r'^[0-9a-f]{64}$')
        for filename in ('index.html', 'gallery.html'):
            for img in Page(filename).root.all('img'):
                if img.attrs.get('src') not in dimensions:
                    continue
                self.assertEqual((int(img.attrs['width']), int(img.attrs['height'])), dimensions[img.attrs['src']])
                for candidate in img.attrs.get('srcset', '').split(','):
                    if candidate.strip():
                        path, width = candidate.split()
                        self.assertEqual(int(width[:-1]), dimensions[path][0])

    def test_source_provenance_optimized_derivatives_and_legacy_preserved(self):
        manifest = ROOT / 'assets/listing/manifest.json'
        self.assertTrue(manifest.exists(), 'listing provenance manifest missing')
        data = json.loads(manifest.read_text())
        self.assertEqual(data['document'], APPROVED['document'])
        self.assertEqual(data['document_sha256'], APPROVED['document_sha256'])
        self.assertEqual(data['approval'], APPROVED['approval'])
        self.assertEqual(data['photos'][5]['provenance'], 'Owner photograph')
        self.assertNotIn('source_url', data['photos'][5])
        self.assertEqual(len(data['photos']), 33)
        for actual, expected in zip(data['photos'], APPROVED['photos']):
            for key in ['position', 'id', 'caption', 'source', 'source_sha256']:
                self.assertEqual(actual[key], expected[key])
            for derivative in actual['derivatives']:
                content = (ROOT / derivative['path']).read_bytes()
                self.assertEqual(hashlib.sha256(content).hexdigest(), derivative['sha256'])
                self.assertLess(len(content), 500_000)
                self.assertEqual(content[8:12], b'WEBP')
        # colonial-yec retires these routes; keep the original approval record intact.
        retired = {'brochure.html', 'floorplans.html', 'sale-prep.html', 'styles.css'}
        for filename, expected in APPROVED['preserved_sha256'].items():
            if filename in retired:
                self.assertFalse((ROOT / filename).exists(), filename)
            else:
                self.assertEqual(hashlib.sha256((ROOT / filename).read_bytes()).hexdigest(), expected, filename)


if __name__ == '__main__':
    unittest.main()
