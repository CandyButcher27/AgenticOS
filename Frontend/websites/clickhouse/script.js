document.querySelectorAll('.faq-row').forEach((row) => {
  row.addEventListener('click', () => {
    const expanded = row.getAttribute('aria-expanded') === 'true';
    document.querySelectorAll('.faq-row').forEach((r) => {
      if (r !== row) {
        r.setAttribute('aria-expanded', 'false');
        r.querySelector('.faq-row__chevron').textContent = '+';
      }
    });
    row.setAttribute('aria-expanded', String(!expanded));
    row.querySelector('.faq-row__chevron').textContent = expanded ? '+' : '×';
  });
});

const hamburger = document.querySelector('.nav-hamburger');
const mobileNav = document.querySelector('.top-nav__mobile');

if (hamburger && mobileNav) {
  hamburger.addEventListener('click', () => {
    const isOpen = mobileNav.classList.toggle('open');
    hamburger.setAttribute('aria-expanded', String(isOpen));
  });
}
