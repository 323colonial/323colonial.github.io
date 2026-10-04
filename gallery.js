const links = [...document.querySelectorAll('[data-gallery-image]')];
const viewer = document.querySelector('#photo-viewer');
const image = document.querySelector('#viewer-image');
const caption = document.querySelector('#viewer-caption');
const title = document.querySelector('#viewer-title');
const fullSize = document.querySelector('#full-size');
const error = document.querySelector('#viewer-error');
const previews = [];
let current = 0;
let opener;

function showPhoto(index) {
  current = (index + links.length) % links.length;
  const link = links[current];
  const thumbnail = link.querySelector('img');
  error.hidden = true;
  image.alt = thumbnail.alt;
  image.src = link.getAttribute('href');
  fullSize.href = link.getAttribute('href');
  caption.replaceChildren(...[...link.parentElement.querySelector('figcaption').children]
    .filter(child => !child.classList.contains('photo-number'))
    .map(child => child.cloneNode(true)));
  title.textContent = `Photo ${current + 1} of ${links.length}`;
  previews.forEach((preview, side) => {
    const adjacent = links[(current + (side === 0 ? -1 : 1) + links.length) % links.length];
    // Placeholder and concept images belong beside their full disclosure, never in a tiny preview.
    preview.hidden = Boolean(adjacent.parentElement.querySelector('.photo-note'));
    if (!preview.hidden) preview.src = adjacent.querySelector('img').getAttribute('src');
  });
}

// Keep ordinary image links working with no JS or without native dialog support.
if (typeof viewer.showModal === 'function') {
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
  image.addEventListener('error', () => { error.hidden = false; });
  image.addEventListener('load', () => { error.hidden = true; });
}

const catalog = document.querySelector('#all-photos');
if (catalog && typeof catalog.showModal === 'function') {
  let catalogOpener;
  document.querySelectorAll('[data-all-photos]').forEach(link => {
    link.addEventListener('click', event => {
      if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      catalogOpener = link;
      catalog.showModal();
    });
  });
  catalog.addEventListener('close', () => catalogOpener?.focus({preventScroll: true}));
}
