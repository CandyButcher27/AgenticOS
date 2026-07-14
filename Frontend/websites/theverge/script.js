const hamburger = document.querySelector('.hamburger');
const drawer = document.getElementById('mobileDrawer');

hamburger.addEventListener('click', () => {
  const expanded = hamburger.getAttribute('aria-expanded') === 'true';
  hamburger.setAttribute('aria-expanded', String(!expanded));
  drawer.classList.toggle('is-open');
});

const form = document.getElementById('newsletterForm');
const note = document.getElementById('formNote');

form.addEventListener('submit', (e) => {
  e.preventDefault();
  note.textContent = 'Thanks — check your inbox to confirm.';
  form.reset();
});
