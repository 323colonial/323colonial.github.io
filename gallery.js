const links = [...document.querySelectorAll('[data-gallery-image]')];
const viewer = document.querySelector('#photo-viewer');
const image = document.querySelector('#viewer-image');
const caption = document.querySelector('#viewer-caption');
const title = document.querySelector('#viewer-title');
const fullSize = document.querySelector('#full-size');
const error = document.querySelector('#viewer-error');
const previews = [];
const viewerDots = createPhotoDots(links.length);

// Decorative position marks; existing text retains the accessible position.
function createPhotoDots(count, current = 0) {
  const dots = document.createElement('span');
  dots.className = 'photo-dots';
  dots.setAttribute('aria-hidden', 'true');
  for (let i = 0; i < count; i++) {
    const dot = document.createElement('span');
    dot.classList.toggle('is-current', i === current);
    dots.append(dot);
  }
  return dots;
}
let current = 0;
let opener;

function photoInset(source, width, height) {
  const photoHeight = width * Number(source.getAttribute('height')) / Number(source.getAttribute('width'));
  return Math.max(0, (height - photoHeight) / 2);
}

function positionViewerDots() {
  if (!viewer.open) return;
  const source = links[current].querySelector('img');
  viewerDots.style.bottom = `${10 + photoInset(source, image.clientWidth, image.clientHeight)}px`;
  const photoWidth = Math.min(image.clientWidth, image.clientHeight * Number(source.getAttribute('width')) / Number(source.getAttribute('height')));
  viewerDots.style.setProperty('--dot-scale', Math.min(1, (photoWidth - 20) / viewerDots.offsetWidth));
}

function showPhoto(index) {
  current = (index + links.length) % links.length;
  const link = links[current];
  const thumbnail = link.querySelector('img');
  error.textContent = 'Loading photo…';
  error.hidden = false;
  // Browsers retain the previous pixels until the new source loads.
  image.style.visibility = 'hidden';
  image.alt = thumbnail.alt;
  image.src = link.getAttribute('href');
  fullSize.href = link.getAttribute('href');
  caption.replaceChildren(...[...link.parentElement.querySelector('figcaption').children]
    .filter(child => !child.classList.contains('photo-number'))
    .map(child => child.cloneNode(true)));
  title.textContent = `Photo ${current + 1} of ${links.length}`;
  [...viewerDots.children].forEach((dot, i) => dot.classList.toggle('is-current', i === current));
  positionViewerDots();
  previews.forEach((preview, side) => {
    const adjacent = links[(current + (side === 0 ? -1 : 1) + links.length) % links.length];
    // Placeholder and concept images belong beside their full disclosure, never in a tiny preview.
    preview.hidden = Boolean(adjacent.parentElement.querySelector('.photo-note'));
    if (!preview.hidden) preview.src = adjacent.querySelector('img').getAttribute('src');
  });
}

// Keep ordinary image links working with no JS or without native dialog support.
if (typeof viewer.showModal === 'function') {
  image.parentElement.append(viewerDots);
  ['previous-photo', 'next-photo'].forEach((id, side) => {
    const preview = new Image(64, 48);
    preview.alt = '';
    preview.className = 'viewer-preview';
    preview.addEventListener('error', () => { preview.hidden = true; });
    document.getElementById(id).insertAdjacentElement(side === 0 ? 'afterbegin' : 'beforeend', preview);
    previews.push(preview);
  });
  const triggers = [...links, ...document.querySelectorAll('[data-photo]')];
  triggers.forEach(link => {
    const index = link.hasAttribute('data-photo') ? Number(link.dataset.photo) - 1 : links.indexOf(link);
    link.addEventListener('click', event => {
      if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      opener = link;
      showPhoto(index);
      viewer.showModal();
      positionViewerDots();
    });
  });
  document.querySelector('#previous-photo').addEventListener('click', () => showPhoto(current - 1));
  document.querySelector('#next-photo').addEventListener('click', () => showPhoto(current + 1));
  viewer.addEventListener('keydown', event => {
    if (event.altKey || event.ctrlKey || event.metaKey || event.shiftKey) return;
    if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
      event.preventDefault();
      showPhoto(current + (event.key === 'ArrowLeft' ? -1 : 1));
    }
  });
  viewer.addEventListener('close', () => opener?.focus({preventScroll: true}));
  image.addEventListener('error', () => {
    error.textContent = 'Image could not load. Try opening the full-size image directly.';
    error.hidden = false;
  });
  image.addEventListener('load', () => {
    error.hidden = true;
    image.style.visibility = 'visible';
    positionViewerDots();
  });
  addEventListener('resize', positionViewerDots);
}

const catalog = document.querySelector('#all-photos');
if (catalog && typeof catalog.showModal === 'function') {
  links.forEach((link, i) => link.append(createPhotoDots(links.length, i)));
  const positionCatalogDots = () => {
    if (!catalog.open) return;
    links.forEach(link => {
      const img = link.querySelector('img');
      const dots = link.querySelector('.photo-dots');
      dots.style.bottom = `${10 + photoInset(img, img.clientWidth, img.clientHeight)}px`;
      const photoWidth = Math.min(img.clientWidth, img.clientHeight * Number(img.getAttribute('width')) / Number(img.getAttribute('height')));
      dots.style.setProperty('--dot-scale', Math.min(1, (photoWidth - 20) / dots.offsetWidth));
    });
  };
  addEventListener('resize', positionCatalogDots);
  let catalogOpener;
  document.querySelectorAll('[data-all-photos]').forEach(link => {
    link.addEventListener('click', event => {
      if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      catalogOpener = link;
      catalog.showModal();
      positionCatalogDots();
    });
  });
  catalog.addEventListener('close', () => catalogOpener?.focus({preventScroll: true}));
}
