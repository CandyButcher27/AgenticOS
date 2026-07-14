const hamburger = document.querySelector('.top-nav__hamburger');
const menu = document.querySelector('.top-nav__menu');

if (hamburger && menu) {
  hamburger.addEventListener('click', () => {
    const isOpen = menu.classList.toggle('is-open');
    hamburger.setAttribute('aria-expanded', String(isOpen));
  });
}

document.querySelectorAll('.newsletter-band__form').forEach((form) => {
  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const input = form.querySelector('.text-input');
    if (input && input.value) {
      input.value = '';
      input.placeholder = 'Thank you for subscribing';
    }
  });
});
