const masthead = document.querySelector('.masthead');
const summary = document.querySelector('.listing-summary');
const stories = [...document.querySelectorAll('.story')];
const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
const narrow = matchMedia('(max-width: 800px)');
let tracks = [];
let pending = false;

function updatePhotos() {
  pending = false;
  for (const track of tracks) {
    const top = track.story.getBoundingClientRect().top + scrollY;
    const index = Math.max(0, Math.min(track.photos.length - 1,
      Math.floor((scrollY - top - track.offset + track.stickyTop) / track.step + .25)));
    // Keep a keyboard user's focused image available until focus leaves it.
    if (track.photos.some(photo => photo.contains(document.activeElement))) continue;
    track.photos.forEach((photo, i) => { photo.hidden = i !== index; });
    track.counter.textContent = `${index + 1} / ${track.photos.length}`;
    // Load the next frame before its scroll threshold, without eager-loading the full gallery.
    const next = track.photos[index + 1]?.querySelector('img');
    if (next) next.loading = 'eager';
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
    photos.forEach(photo => { photo.hidden = false; });
    const cue = story.querySelector('.scroll-cue');
    cue.hidden = true;
    const stickyTop = headerHeight + summaryHeight + (narrow.matches ? 16 : 24);
    const available = innerHeight - stickyTop - 32;
    const copyHeight = story.querySelector('.story-copy').getBoundingClientRect().height;
    // Short windows and reduced motion use ordinary, fully visible photographs.
    if (reducedMotion.matches || available < 300 || (!narrow.matches && copyHeight > available)) continue;
    const photoWidth = story.querySelector('.story-photos').getBoundingClientRect().width;
    story.style.setProperty('--photo-height', `${Math.min(available - 110, photoWidth * .75)}px`);
    photos.forEach((photo, i) => { photo.hidden = i !== 0; });
    cue.hidden = false;
    story.classList.add('is-scrolling');
    const stage = story.querySelector(narrow.matches ? '.story-photos' : '.story-stage');
    const padding = parseFloat(getComputedStyle(story).paddingTop);
    const offset = padding + (narrow.matches ? copyHeight + 28 : 0);
    const step = Math.max(240, innerHeight * .5);
    const height = offset + stage.getBoundingClientRect().height + padding + (photos.length - 1) * step;
    story.style.setProperty('--story-height', `${height}px`);
    tracks.push({story, photos, stickyTop, offset, step, counter: cue.querySelector('.slide-count')});
  }
  updatePhotos();
}

addEventListener('scroll', () => {
  if (!pending) { pending = true; requestAnimationFrame(updatePhotos); }
}, {passive: true});
addEventListener('resize', layoutStories);
reducedMotion.addEventListener('change', layoutStories);
const headerObserver = new ResizeObserver(layoutStories);
headerObserver.observe(masthead);
if (summary) headerObserver.observe(summary);
document.fonts.ready.then(layoutStories);
layoutStories();

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
