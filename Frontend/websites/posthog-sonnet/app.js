(function () {
  const hamburger = document.getElementById('hamburger');
  const drawer = document.getElementById('mobile-drawer');

  function closeDrawer() {
    drawer.classList.remove('open');
    hamburger.setAttribute('aria-expanded', 'false');
  }

  hamburger.addEventListener('click', () => {
    const isOpen = drawer.classList.toggle('open');
    hamburger.setAttribute('aria-expanded', String(isOpen));
  });

  drawer.querySelectorAll('a').forEach((link) => {
    link.addEventListener('click', closeDrawer);
  });

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeDrawer();
  });

  const backToTop = document.getElementById('back-to-top');
  window.addEventListener('scroll', () => {
    backToTop.classList.toggle('visible', window.scrollY > 600);
  });
  backToTop.addEventListener('click', () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });

  const searchToggle = document.getElementById('search-toggle');
  searchToggle.addEventListener('click', () => {
    alert('Search is a static homage — no live search index here.');
  });
})();
