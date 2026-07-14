document.querySelectorAll('.faq-row').forEach((row) => {
  row.addEventListener('click', () => {
    const expanded = row.getAttribute('aria-expanded') === 'true';
    document.querySelectorAll('.faq-row').forEach((r) => r.setAttribute('aria-expanded', 'false'));
    row.setAttribute('aria-expanded', String(!expanded));
  });
});

const cookieConsent = document.getElementById('cookieConsent');
const cookieAgree = document.getElementById('cookieAgree');
if (cookieAgree) {
  cookieAgree.addEventListener('click', (e) => {
    e.preventDefault();
    cookieConsent.classList.add('is-dismissed');
  });
}

const frap = document.querySelector('.frap');
if (frap) {
  frap.addEventListener('click', () => {
    document.querySelector('.hero')?.scrollIntoView({ behavior: 'smooth' });
  });
}
