(() => {
  const hero = document.querySelector('.hero-photo a[data-seasons]');
  const button = document.querySelector('#hero-motion');
  if (!hero || !button || !hero.animate || !CSS.supports('mix-blend-mode', 'plus-lighter') || navigator.connection?.saveData) return;
  const original = hero.querySelector('img');
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const print = matchMedia('print');
  let animations = [], loading = false, paused = false, visible = false;

  function sync() {
    const staticPhoto = reduced.matches || print.matches;
    hero.classList.toggle('seasonal-static', staticPhoto);
    button.hidden = !animations.length || staticPhoto;
    const play = !paused && !staticPhoto && visible && !document.hidden && !document.querySelector('dialog[open]');
    animations.forEach(animation => {
      if (play && animation.playState !== 'running') animation.play();
      if (!play && animation.playState !== 'paused') animation.pause();
    });
    if (!staticPhoto && visible) load();
  }

  async function load() {
    if (loading || !original.complete || !original.naturalWidth) return;
    loading = true;
    const layers = hero.dataset.seasons.split(' ').map(src => {
      const image = new Image(1280, 848);
      image.alt = '';
      image.className = 'hero-season';
      image.decoding = 'async';
      image.fetchPriority = 'low';
      image.src = src;
      return image;
    });
    try {
      await Promise.all(layers.map(image => image.decode()));
      hero.append(...layers);
      const images = [original, ...layers], count = images.length;
      images.forEach((image, index) => {
        const animation = image.animate([
          {opacity: 1, offset: 0}, {opacity: 0, offset: 1 / count},
          {opacity: 0, offset: 1 - 1 / count}, {opacity: 1, offset: 1},
        ], {duration: 24000, iterations: Infinity, delay: -((count - index) % count) * 24000 / count});
        animation.pause();
        animation.currentTime = 0;
        animations.push(animation);
      });
      hero.classList.add('seasonal-ready');
      hero.setAttribute('aria-description', 'Animated seasonal concept. Opens the original property photograph.');
      sync();
    } catch {
      animations.forEach(animation => animation.cancel());
      animations = [];
      layers.forEach(image => image.remove());
      // Original photograph remains usable if any seasonal frame cannot decode.
    }
  }

  button.addEventListener('click', () => {
    paused = !paused;
    button.textContent = paused ? 'Resume animation' : 'Pause animation';
    sync();
  });
  new IntersectionObserver(([entry]) => { visible = entry.isIntersecting; sync(); }).observe(hero);
  const dialogs = new MutationObserver(sync);
  document.querySelectorAll('dialog').forEach(dialog => dialogs.observe(dialog, {attributes: true, attributeFilter: ['open']}));
  document.addEventListener('visibilitychange', sync);
  reduced.addEventListener('change', sync);
  print.addEventListener('change', sync);
  original.addEventListener('load', sync, {once: true});
  sync();
})();
