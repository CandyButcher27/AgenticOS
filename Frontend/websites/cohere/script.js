const navShell = document.querySelector('.nav-shell');
const navToggle = document.querySelector('.nav-toggle');
const navLinks = document.querySelectorAll('.nav-links a');

if (navToggle && navShell) {
  navToggle.addEventListener('click', () => {
    const isOpen = navShell.classList.toggle('is-open');
    navToggle.setAttribute('aria-expanded', String(isOpen));
  });
}

navLinks.forEach((link) => {
  link.addEventListener('click', () => {
    if (!navShell || !navToggle) {
      return;
    }

    navShell.classList.remove('is-open');
    navToggle.setAttribute('aria-expanded', 'false');
  });
});