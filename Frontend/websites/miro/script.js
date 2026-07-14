document.querySelectorAll('.faq-row').forEach((row) => {
  row.addEventListener('click', () => {
    const expanded = row.getAttribute('aria-expanded') === 'true';
    document.querySelectorAll('.faq-row').forEach((r) => r.setAttribute('aria-expanded', 'false'));
    document.querySelectorAll('.faq-row__chevron').forEach((c) => c.textContent = '＋');
    if (!expanded) {
      row.setAttribute('aria-expanded', 'true');
      row.querySelector('.faq-row__chevron').textContent = '－';
    }
  });
});

document.querySelectorAll('.pill-tab').forEach((tab) => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.pill-tab').forEach((t) => t.classList.remove('pill-tab--active'));
    tab.classList.add('pill-tab--active');
  });
});

document.querySelectorAll('.toggle-pill').forEach((pill) => {
  pill.addEventListener('click', () => {
    document.querySelectorAll('.toggle-pill').forEach((p) => p.classList.remove('toggle-pill--active'));
    pill.classList.add('toggle-pill--active');
  });
});

const hamburger = document.querySelector('.hamburger');
if (hamburger) {
  hamburger.addEventListener('click', () => {
    document.querySelector('.top-nav').classList.toggle('top-nav--open');
  });
}
