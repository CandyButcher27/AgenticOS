document.querySelectorAll('.faq-row').forEach((row) => {
  row.addEventListener('click', () => {
    const expanded = row.getAttribute('aria-expanded') === 'true';

    document.querySelectorAll('.faq-row').forEach((other) => {
      if (other !== row) {
        other.setAttribute('aria-expanded', 'false');
        other.querySelector('.faq-row__chevron').textContent = '＋';
      }
    });

    row.setAttribute('aria-expanded', String(!expanded));
    row.querySelector('.faq-row__chevron').textContent = expanded ? '＋' : '－';
  });
});

const hamburger = document.querySelector('.hamburger');
const mobileNav = document.querySelector('.mobile-nav');

if (hamburger && mobileNav) {
  hamburger.addEventListener('click', () => {
    const isOpen = mobileNav.classList.toggle('is-open');
    hamburger.setAttribute('aria-expanded', String(isOpen));
  });
}
