const masthead = document.querySelector('.masthead');
const summary = document.querySelector('.listing-summary');
const stories = [...document.querySelectorAll('.story')];
const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
const narrow = matchMedia('(max-width: 800px)');
let tracks = [];
let pending = false;
let focusedPhoto;

function updatePhotos() {
  pending = false;
  // A modal borrows focus; keep its photo opener available for native focus restoration.
  if (!document.querySelector('dialog[open]')) {
    focusedPhoto = document.activeElement.closest('.story-photos figure');
  }
  for (const track of tracks) {
    const bounds = track.story.getBoundingClientRect();
    const top = bounds.top + scrollY;
    const position = Math.max(0, Math.min(track.photos.length - 1,
      (scrollY - top - track.offset + track.stickyTop) / track.step));
    // Hold each photo for half a step, then blend directly with scroll (no timed easing).
    const focused = track.photos.indexOf(focusedPhoto);
    const progress = focused < 0
      ? Math.floor(position) + Math.max(0, (position % 1 - .5) * 2) : focused;
    const index = Math.round(progress);
    track.photos.forEach((photo, i) => {
      const opacity = Math.max(0, 1 - Math.abs(i - progress));
      photo.hidden = opacity === 0;
      photo.style.setProperty('--photo-opacity', opacity);
      photo.inert = i !== index;
      photo.setAttribute('aria-hidden', String(i !== index));
    });
    track.counter.textContent = `${index + 1} / ${track.photos.length}`;
    // Preload only nearby sequences, not the next frame of every distant story.
    const next = track.photos[index + 1]?.querySelector('img');
    if (next && bounds.top < innerHeight * 2 && bounds.bottom > 0) next.loading = 'eager';
  }
}

function layoutStories() {
  const headerHeight = masthead.getBoundingClientRect().height;
  const summaryHeight = summary?.getBoundingClientRect().height || 0;
  document.documentElement.style.setProperty('--header-height', `${headerHeight}px`);
  document.documentElement.style.setProperty('--summary-height', `${summaryHeight}px`);
  tracks = [];
  for (const story of stories) {
    story.classList.remove('is-scrolling');
    const photos = [...story.querySelectorAll('.story-photos figure')];
    story.style.removeProperty('--frame-height');
    photos.forEach(photo => {
      photo.hidden = false;
      photo.style.removeProperty('--photo-opacity');
      photo.inert = false;
      photo.removeAttribute('aria-hidden');
    });
    const cue = story.querySelector('.scroll-cue');
    cue.hidden = true;
    const stickyTop = headerHeight + summaryHeight + (narrow.matches ? 16 : 24);
    const available = innerHeight - stickyTop - 32;
    const copyHeight = story.querySelector('.story-copy').getBoundingClientRect().height;
    // Short windows and reduced motion use ordinary, fully visible photographs.
    if (reducedMotion.matches || available < 300 || (!narrow.matches && copyHeight > available)) continue;
    const photoWidth = story.querySelector('.story-photos').getBoundingClientRect().width;
    story.style.setProperty('--photo-height', `${Math.min(available - 110, photoWidth * .75)}px`);
    cue.hidden = false;
    story.classList.add('is-scrolling');
    // Reserve the tallest caption as well as the image, so blending never shifts the stage.
    story.style.setProperty('--frame-height', `${Math.max(...photos.map(photo => photo.getBoundingClientRect().height))}px`);
    const stage = story.querySelector(narrow.matches ? '.story-photos' : '.story-stage');
    const padding = parseFloat(getComputedStyle(story).paddingTop);
    const offset = padding + (narrow.matches ? copyHeight + 28 : 0);
    const step = Math.max(240, innerHeight * .5);
    // The final photo gets a full viewing step after its blend has finished.
    const height = offset + stage.getBoundingClientRect().height + padding + photos.length * step;
    story.style.setProperty('--story-height', `${height}px`);
    tracks.push({story, photos, stickyTop, offset, step, counter: cue.querySelector('.slide-count')});
  }
  updatePhotos();
}

addEventListener('scroll', () => {
  if (!pending) { pending = true; requestAnimationFrame(updatePhotos); }
}, {passive: true});
document.addEventListener('focusin', updatePhotos);
document.addEventListener('focusout', () => requestAnimationFrame(updatePhotos));
addEventListener('resize', layoutStories);
reducedMotion.addEventListener('change', layoutStories);
const headerObserver = new ResizeObserver(layoutStories);
headerObserver.observe(masthead);
if (summary) headerObserver.observe(summary);
document.fonts.ready.then(layoutStories);
layoutStories();

const detailsDialog = document.querySelector('#property-details');
const priceLink = document.querySelector('.price a');
if (detailsDialog && typeof detailsDialog.showModal === 'function') {
  detailsDialog.append(document.querySelector('#details .detail-grid').cloneNode(true));
  priceLink.setAttribute('aria-haspopup', 'dialog');
  priceLink.addEventListener('click', event => {
    if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    detailsDialog.showModal();
  });
  detailsDialog.addEventListener('close', () => priceLink.focus({preventScroll: true}));
}

const contact = document.querySelector('.showing-contact');
document.addEventListener('keydown', event => {
  if (event.key === 'Escape' && contact.open && !document.querySelector('dialog[open]')) {
    contact.open = false;
    contact.querySelector('summary').focus();
  }
});
document.addEventListener('click', event => {
  if (!contact.contains(event.target)) contact.open = false;
});
