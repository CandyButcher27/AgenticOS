document.querySelectorAll('.faq-row').forEach((row) => {
  const toggle = () => {
    const expanded = row.getAttribute('aria-expanded') === 'true';
    row.setAttribute('aria-expanded', String(!expanded));
  };
  row.addEventListener('click', toggle);
  row.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      toggle();
    }
  });
});

document.querySelectorAll('.category-tab-group .category-tab').forEach((tab) => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.category-tab-group .category-tab').forEach((t) => {
      t.classList.remove('category-tab-active');
    });
    tab.classList.add('category-tab-active');
  });
});

const hamburger = document.querySelector('.hamburger');
const drawer = document.querySelector('.mobile-drawer');
if (hamburger && drawer) {
  hamburger.addEventListener('click', () => {
    const isOpen = drawer.classList.toggle('is-open');
    hamburger.setAttribute('aria-expanded', String(isOpen));
    drawer.setAttribute('aria-hidden', String(!isOpen));
  });
}
