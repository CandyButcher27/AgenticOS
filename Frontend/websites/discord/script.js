document.querySelectorAll('.faq-accordion').forEach((row) => {
  row.addEventListener('click', () => {
    const expanded = row.getAttribute('aria-expanded') === 'true';
    row.setAttribute('aria-expanded', String(!expanded));
    row.querySelector('.faq-accordion__chevron').textContent = expanded ? '＋' : '－';
  });
});

const hamburger = document.getElementById('hamburger');
if (hamburger) {
  hamburger.addEventListener('click', () => {
    document.querySelector('.nav-bar__links').classList.toggle('nav-bar__links--open');
    document.querySelector('.nav-bar__actions').classList.toggle('nav-bar__actions--open');
  });
}
