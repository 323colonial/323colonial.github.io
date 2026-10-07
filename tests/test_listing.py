"""Approved listing copy, gallery, asset and preservation contract. No dependencies."""
import hashlib
import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import unittest

ROOT = Path(__file__).resolve().parents[1]
APPROVED = json.loads((ROOT / 'tests/fixtures/approved-listing.json').read_text())
COVERAGE = json.loads((ROOT / 'tests/fixtures/photo-coverage.json').read_text())
REDFIN = json.loads((ROOT / 'tests/fixtures/redfin-refresh.json').read_text())


def before_redfin(photo):
    """Recover frozen historical record; replacement provenance never rewrites it."""
    original = dict(photo)
    replacement = original.pop('redfin_source', None)
    if replacement:
        original['derivatives'] = replacement['previous_derivatives']
    return original


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
        self.assertEqual(covered, set(range(1, 74)), 'Every photo has a narrative home')
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
        self.assertEqual(len(figures), 73)
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

    def test_additional_interiors_in_context_and_both_galleries(self):
        additions = [
            (34, '55.jpg', 0, 'Wood staircase and detailed trim in the entry.'),
            (35, '42.jpg', 1, 'Kitchen island looking toward the dining area and great room.'),
            (36, '50.jpg', 3, 'Main-level half bath with wood vanity and window.'),
            (37, '51.jpg', 3, 'Main-floor primary bedroom looking toward the closet and adjoining bath.'),
            (38, '61.jpg', 3, 'Upstairs full bath with tub and shower.'),
        ]
        source_hashes = [
            'f3a340d795d9f66ebbde4abf7fa7687d8aabfa6fc83cf20245a067b849353d0b',
            'f136887a7a2b6fed9a5f31eaa2c6c63e2e5e1633df526a7bf6a41d1fee6e3c36',
            '35c13faf7d3ed5eb0bdbc6aa246bee42e2b1c70b214a814b3a8d8cee76384fdb',
            '3edbb69bf843e13a158060562bbd64637a16618ee3b1ed3afd45c4040b5fe6db',
            '9e802289f86d1a69261f1eb50fbf75527765e0ff6e010e5182aed35370db2fb5',
        ]
        home = Page('index.html').root
        stories = [s for s in home.all('section') if s.cls('story')]
        self.assertIn('View all 73 photos', home.text())
        self.assertIn('All 73 photos', home.text())
        photos = json.loads((ROOT / 'assets/listing/manifest.json').read_text())['photos']
        for file in ('index.html', 'gallery.html'):
            grid = next(d for d in Page(file).root.all('div') if d.cls('gallery-grid'))
            self.assertEqual([int(f.attrs['data-position']) for f in grid.all('figure')], list(range(1, 74)))
            for figure in grid.all('figure'):
                number = next(s for s in figure.all('span') if s.cls('photo-number'))
                self.assertEqual(number.text(), f"{figure.attrs['data-position']} / 73")
            for n, source, section, caption in additions:
                figure = next(f for f in grid.all('figure') if f.attrs['data-position'] == str(n))
                inline = [f for f in stories[section].all('figure') if f.attrs['data-position'] == str(n)]
                self.assertEqual(len(inline), 1, f'Photo {n} needs its contextual narrative home')
                for record in (figure, inline[0]):
                    self.assertEqual(record.all('img')[0].attrs['alt'], caption)
                    self.assertEqual(next(s for s in record.all('span') if s.cls('caption-text')).text(), caption)
                    image = record.all('img')[0]
                    self.assertEqual(image.attrs['loading'], 'lazy')
                    self.assertEqual(image.attrs['decoding'], 'async')
                    self.assertEqual(image.attrs['srcset'], f'assets/listing/{n}-small.webp 720w, assets/listing/{n}.webp 1440w')
                    self.assertTrue(image.attrs['sizes'])
                    self.assertEqual(record.all('a')[0].attrs['aria-label'], f'Enlarge photo {n}: {caption}')
                self.assertEqual(figure.all('a')[0].attrs['href'], f'assets/listing/{n}.webp')
                self.assertEqual(inline[0].all('a')[0].attrs['href'], f'gallery.html#photo-{n}')
                photo = photos[n - 1]
                self.assertEqual(photo['source'], f'listing info/pics/{source}')
                self.assertEqual(photo['source_sha256'], source_hashes[n - 34])
                self.assertEqual(photo['caption'], caption)
                self.assertEqual(photo['crop_xywh'], None)
                self.assertEqual([d['width'] for d in photo['derivatives']], [1440, 720])

    def test_complete_source_inventory_and_expanded_coverage(self):
        sources = COVERAGE['sources']
        listing = [r for r in sources if r['source'].startswith('listing info/pics/')]
        self.assertEqual([r['source'] for r in listing], [f'listing info/pics/{n}.jpg' for n in range(1, 78)])
        self.assertEqual(len(sources), 82)
        photos = json.loads((ROOT / 'assets/listing/manifest.json').read_text())['photos']
        self.assertEqual(hashlib.sha256(json.dumps([before_redfin(p) for p in photos[:38]], sort_keys=True).encode()).hexdigest(),
                         COVERAGE['baseline_photos_sha256'], 'All original 38 records must remain unchanged')
        additions = [r for r in sources if r['status'] == 'add']
        self.assertEqual([r['position'] for r in additions], list(range(39, 74)))
        for row in sources:
            self.assertIn(row['status'], ('represented', 'omitted', 'add'))
            self.assertIn(row['section'], range(1, 8))
            self.assertTrue(row['reason'])
            self.assertRegex(row['sha256'], r'^[0-9a-f]{64}$')
            if row['status'] != 'add':
                self.assertTrue(row['matches'])
            if row['source'] in [f'listing info/pics/{n}.jpg' for n in range(62, 66)]:
                self.assertEqual(row['status'], 'omitted', 'Owner excludes older basement photographs')
        stories = [s for s in Page('index.html').root.all('section') if s.cls('story')]
        for file in ('index.html', 'gallery.html'):
            grid = next(d for d in Page(file).root.all('div') if d.cls('gallery-grid'))
            figures = grid.all('figure')
            self.assertEqual([int(f.attrs['data-position']) for f in figures], list(range(1, 74)))
            for row in additions:
                n, caption = row['position'], row['caption']
                photo = photos[n - 1]
                self.assertEqual(photo['source'], row['source'])
                self.assertEqual(photo['source_sha256'], row['sha256'])
                self.assertEqual(photo['source_size'], row['size'])
                self.assertEqual(photo['caption'], caption)
                self.assertEqual(photo['approval'], 'colonial-we3, 2026-10-05')
                self.assertIsNone(photo['crop_xywh'])
                widths = [row['full_width'], 720]
                self.assertEqual([d['width'] for d in photo['derivatives']], widths)
                inline = stories[row['section'] - 1].all('figure')
                positions = [int(f.attrs['data-position']) for f in inline]
                self.assertIn(n, positions)
                self.assertGreater(positions.index(n), positions.index(row['after']))
                for figure in (figures[n - 1], inline[positions.index(n)]):
                    img = figure.all('img')[0]
                    self.assertEqual(img.attrs['alt'], caption)
                    self.assertEqual(img.attrs['loading'], 'lazy')
                    self.assertEqual(img.attrs['decoding'], 'async')
                    self.assertEqual(img.attrs['srcset'], f'assets/listing/{n}-small.webp 720w, assets/listing/{n}.webp {widths[0]}w')
                    self.assertTrue(img.attrs['sizes'])
                    self.assertEqual(next(s for s in figure.all('span') if s.cls('caption-text')).text(), caption)
                    self.assertEqual(figure.all('a')[0].attrs['aria-label'], f'Enlarge photo {n}: {caption}')

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
            listing_links = [a for a in header.all('a') if a.text() == 'Questions & tours']
            self.assertEqual(len(listing_links), 1)
            link = listing_links[0]
            self.assertEqual(link.attrs['href'], 'https://search.soldvawv.com/search/detail/270760671')
            self.assertEqual(link.attrs['aria-label'], 'Questions & tours through Dandridge Realty Group')
            self.assertNotIn('target', link.attrs, 'Keep same-tab navigation')
            self.assertNotIn('redfin', (ROOT / file).read_text().lower())
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

    def test_compact_facts_grouping(self):
        page = Page('index.html').root
        price = next(h for h in page.all('h2') if h.cls('price'))
        self.assertLess(price.text().index('$499,000'), price.text().index('Property details'))
        actions = next(d for d in page.all('div') if d.cls('summary-actions'))
        self.assertLess(actions.text().index('Coming Soon'), actions.text().index('Expected on market'))

    def test_inline_brokerage_contacts_on_both_pages(self):
        for filename in ('index.html', 'gallery.html'):
            page = Page(filename).root
            header = page.all('header')[0]
            self.assertFalse(header.all('details'), 'Contact must not require opening a disclosure')
            contact = next(d for d in header.all('div') if d.cls('header-contact'))
            self.assertEqual(contact.attrs['aria-label'], 'Listing agent contact')
            for detail in ('Liz McDonald', 'Dandridge Realty Group LLC'):
                self.assertEqual(header.text().count(detail), 1, 'Do not duplicate agent identity')
            links = contact.all('a')
            self.assertEqual(len(links), 2, 'Only phone and questions/tours actions')
            self.assertEqual(links[0].attrs['href'], 'tel:+13048851547')
            self.assertEqual(links[0].text(), '(304) 885-1547')
            self.assertEqual(links[0].attrs['aria-label'], 'Call Dandridge office at (304) 885-1547')
            self.assertEqual(links[1].text(), 'Questions & tours')
            self.assertFalse(header.all('button'), 'Contact uses native links, no integration')
            for removed in ('See in person', 'View public listing', 'Email Liz'):
                self.assertNotIn(removed, header.text())
            self.assertNotRegex(page.text().lower(), r'michelle|283-8640|885-7645|fast response')
        printed = next(p for p in Page('index.html').root.all('p') if p.cls('print-contact'))
        self.assertEqual(printed.parent.tag, 'footer')
        self.assertIn('Liz McDonald · Listing agent', printed.text())
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
            for d in photo['derivatives']:
                dimensions[d['path']] = (d['width'], d['height'])
            historical = before_redfin(photo)
            full = historical['derivatives'][0]
            for d in historical['derivatives']:
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

    def test_redfin_refresh_matches_and_preserves_every_other_record(self):
        photos = json.loads((ROOT / 'assets/listing/manifest.json').read_text())['photos']
        matches = {m['position']: m for m in REDFIN['matches']}
        self.assertEqual(len(matches), 26)
        self.assertEqual(len({m['url'] for m in matches.values()}), 26)
        self.assertEqual(set(REDFIN['retained_positions']), set(range(1, 74)) - matches.keys())
        for photo, baseline in zip(photos, REDFIN['baseline_records_sha256']):
            self.assertEqual(hashlib.sha256(json.dumps(before_redfin(photo), sort_keys=True).encode()).hexdigest(), baseline)
            n = photo['position']
            if n not in matches:
                self.assertNotIn('redfin_source', photo)
                continue
            self.assertIn('redfin_source', photo, f'Photo {n} still uses degraded source')
            source, match = photo['redfin_source'], matches[n]
            for key in ('redfin_position', 'file', 'url', 'sha256', 'size', 'visual_match'):
                self.assertEqual(source[key], match[key], f'Photo {n}: wrong {key}')
            self.assertTrue(source['url'].startswith('https://ssl.cdn-redfin.com/photo/235/bigphoto/198/'))
            self.assertIsNone(source['crop_xywh'], 'Keep original framing and watermark')
            self.assertEqual(source['quality'], 80)
            self.assertEqual([d['width'] for d in photo['derivatives']], [1280, 720])
            self.assertEqual([photo['derivatives'][0][k] for k in ('width', 'height')], source['size'])
            self.assertNotEqual(photo['derivatives'], source['previous_derivatives'])
            for d in photo['derivatives']:
                self.assertNotIn('margin_trim', d, 'Screenshot trims must not be reapplied to originals')

    def test_source_provenance_optimized_derivatives_and_legacy_preserved(self):
        manifest = ROOT / 'assets/listing/manifest.json'
        self.assertTrue(manifest.exists(), 'listing provenance manifest missing')
        data = json.loads(manifest.read_text())
        self.assertEqual(data['document'], APPROVED['document'])
        self.assertEqual(data['document_sha256'], APPROVED['document_sha256'])
        self.assertEqual(data['approval'], APPROVED['approval'])
        self.assertEqual(data['photos'][5]['provenance'], 'Owner photograph')
        self.assertNotIn('source_url', data['photos'][5])
        self.assertEqual(len(data['photos']), 73)
        for actual, expected in zip(data['photos'], APPROVED['photos']):
            for key in ['position', 'id', 'caption', 'source', 'source_sha256']:
                self.assertEqual(actual[key], expected[key])
        for actual in data['photos']:
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
