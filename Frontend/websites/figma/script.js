document.querySelectorAll('.faq-row').forEach((row) => {
  row.addEventListener('click', () => {
    const expanded = row.getAttribute('aria-expanded') === 'true';
    row.setAttribute('aria-expanded', String(!expanded));
    row.querySelector('.faq-row__chevron').textContent = expanded ? '＋' : '－';
  });
});

document.querySelectorAll('.pricing-tab').forEach((tab) => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.pricing-tab').forEach((t) => t.classList.remove('pricing-tab--selected'));
    tab.classList.add('pricing-tab--selected');
  });
});

const navHamburger = document.getElementById('navHamburger');
const mobileOverlay = document.getElementById('mobileOverlay');

navHamburger.addEventListener('click', () => {
  const isOpen = mobileOverlay.classList.toggle('open');
  navHamburger.setAttribute('aria-expanded', String(isOpen));
});

mobileOverlay.querySelectorAll('a').forEach((link) => {
  link.addEventListener('click', () => {
    mobileOverlay.classList.remove('open');
    navHamburger.setAttribute('aria-expanded', 'false');
  });
});

document.querySelector('.contact-form')?.addEventListener('submit', (e) => {
  e.preventDefault();
  const button = e.target.querySelector('.contact-form__submit');
  const original = button.textContent;
  button.textContent = 'Message sent';
  setTimeout(() => { button.textContent = original; }, 2000);
});
