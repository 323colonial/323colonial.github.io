const masthead = document.querySelector('.masthead');
const summary = document.querySelector('.listing-summary');
const heroImage = document.querySelector('.hero-photo img');
const stories = [...document.querySelectorAll('.story')];
const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
const narrow = matchMedia('(max-width: 800px)');
let tracks = [];
let pending = false;
let focusedPhoto;

stories.forEach(story => {
  story.querySelector('.scroll-cue').append(createPhotoDots(story.querySelectorAll('.story-photos figure').length));
});

function updatePhotos() {
  pending = false;
  // A modal borrows focus; keep its photo opener available for native focus restoration.
  if (!document.querySelector('dialog[open]')) {
    focusedPhoto = document.activeElement.closest('.story-photos figure');
  }
  // Let the visible hero finish before competing speculative image requests.
  const canPreload = !heroImage || heroImage.complete || heroImage.getBoundingClientRect().bottom <= 0;
  for (const track of tracks) {
    const bounds = track.story.getBoundingClientRect();
    const start = track.story.offsetTop + track.offset - track.stickyTop;
    const distance = scrollY - start;
    // Keep the next section at its exit spacing while this photo sequence is pinned.
    const remaining = Math.max(0, Math.min(track.photos.length * track.step,
      track.photos.length * track.step - distance));
    track.story.nextElementSibling?.style.setProperty('--story-shift', `${-remaining}px`);
    const position = Math.max(0, Math.min(track.photos.length - 1, distance / track.step));
    // Hold each photo for half a step, then blend directly with scroll (no timed easing).
    const focused = track.photos.indexOf(focusedPhoto);
    const progress = focused < 0
      ? Math.floor(position) + Math.max(0, (position % 1 - .5) * 2) : focused;
    const index = Math.round(progress);
    // Holds and distant stories retain their DOM state; layout rebuilds the tracks.
    if (track.progress !== progress) {
      track.photos.forEach((photo, i) => {
        const opacity = Math.max(0, 1 - Math.abs(i - progress));
        photo.hidden = opacity === 0;
        photo.style.setProperty('--photo-opacity', opacity);
        photo.inert = i !== index;
        photo.setAttribute('aria-hidden', String(i !== index));
        track.dots.children[i].classList.toggle('is-current', i === index);
      });
      const count = `${index + 1} / ${track.photos.length}`;
      // Replacing unchanged text forces layout at the next story's geometry read.
      if (track.counter.textContent !== count) track.counter.textContent = count;
      track.dots.style.setProperty('--photo-inset', `${track.insets[index]}px`);
      track.progress = progress;
    }
    // Preload only nearby sequences, not the next frame of every distant story.
    const next = track.photos[index + 1]?.querySelector('img');
    if (next && canPreload && bounds.top < innerHeight * 2 && bounds.bottom > 0) next.loading = 'eager';
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
    story.style.removeProperty('--story-shift');
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
    const style = getComputedStyle(story);
    const borderHeight = parseFloat(style.getPropertyValue('--border-lines')) * parseFloat(style.lineHeight);
    if (story.previousElementSibling) {
      story.style.setProperty('--previous-story-color', getComputedStyle(story.previousElementSibling).backgroundColor);
    }
    const stickyTop = headerHeight + summaryHeight + borderHeight + (narrow.matches ? 16 : 24);
    const available = innerHeight - stickyTop - 32;
    const copyHeight = story.querySelector('.story-copy').getBoundingClientRect().height;
    // Short windows and reduced motion use ordinary, fully visible photographs.
    if (reducedMotion.matches || available < 300 || (!narrow.matches && copyHeight > available)) continue;
    const photoWidth = story.querySelector('.story-photos').getBoundingClientRect().width;
    const photoHeight = Math.min(available - 110, photoWidth * .75);
    story.style.setProperty('--photo-height', `${photoHeight}px`);
    const insets = photos.map(photo => photoInset(photo.querySelector('img'), photoWidth, photoHeight));
    cue.hidden = false;
    story.classList.add('is-scrolling');
    // Reserve the tallest caption as well as the image, so blending never shifts the stage.
    story.style.setProperty('--frame-height', `${Math.max(...photos.map(photo => photo.getBoundingClientRect().height))}px`);
    const stage = story.querySelector(narrow.matches ? '.story-photos' : '.story-stage');
    const padding = parseFloat(getComputedStyle(story).paddingTop);
    const offset = padding + borderHeight + (narrow.matches ? copyHeight + 28 : 0);
    const step = Math.max(240, innerHeight * .5);
    // The final photo gets a full viewing step after its blend has finished.
    const height = offset + stage.getBoundingClientRect().height + padding + photos.length * step;
    story.style.setProperty('--story-height', `${height}px`);
    tracks.push({story, photos, insets, stickyTop, offset, step, counter: cue.querySelector('.slide-count'), dots: cue.querySelector('.photo-dots')});
  }
  updatePhotos();
}

heroImage?.addEventListener('load', updatePhotos);
heroImage?.addEventListener('error', updatePhotos);
addEventListener('scroll', () => {
  if (!pending) { pending = true; requestAnimationFrame(updatePhotos); }
}, {passive: true});
document.addEventListener('focusin', event => {
  updatePhotos();
  const story = event.target.closest('.story');
  const shift = parseFloat(story?.style.getPropertyValue('--story-shift')) || 0;
  const bounds = event.target.getBoundingClientRect();
  // Native focus scrolling cannot reach an offscreen link in a pinned preview.
  if (shift < 0 && bounds.bottom > innerHeight) {
    const borderHeight = parseFloat(getComputedStyle(story, '::before').height) || 0;
    const clearance = parseFloat(getComputedStyle(document.documentElement).scrollPaddingTop) + borderHeight;
    scrollTo(0, scrollY + bounds.top - shift - clearance);
    updatePhotos();
  }
});
document.addEventListener('focusout', () => requestAnimationFrame(updatePhotos));
addEventListener('resize', layoutStories);
reducedMotion.addEventListener('change', layoutStories);
const headerObserver = new ResizeObserver(entries => {
  // Window resize already lays out stories; only new header heights need another pass.
  if (entries.some(({target}) => target.getBoundingClientRect().height !== parseFloat(
    document.documentElement.style.getPropertyValue(target === masthead ? '--header-height' : '--summary-height')
  ))) layoutStories();
});
headerObserver.observe(masthead);
if (summary) headerObserver.observe(summary);
document.fonts.ready.then(layoutStories);
layoutStories();

const detailsDialog = document.querySelector('#property-details');
const detailsLink = document.querySelector('.price a');
if (detailsDialog && typeof detailsDialog.showModal === 'function') {
  detailsDialog.append(document.querySelector('#details .detail-grid').cloneNode(true));
  detailsLink.setAttribute('aria-haspopup', 'dialog');
  detailsLink.addEventListener('click', event => {
    if (event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    detailsDialog.showModal();
  });
  detailsDialog.addEventListener('close', () => detailsLink.focus({preventScroll: true}));
  document.querySelector('#details').classList.add('has-dialog');
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
