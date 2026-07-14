document.querySelectorAll('.faq-row').forEach((row) => {
  row.addEventListener('click', () => {
    const expanded = row.getAttribute('aria-expanded') === 'true';
    row.setAttribute('aria-expanded', String(!expanded));
    row.querySelector('.faq-row__chevron').textContent = expanded ? '＋' : '－';
  });
});

document.querySelectorAll('.configurator-swatch').forEach((swatch) => {
  swatch.addEventListener('click', () => {
    const siblings = swatch.closest('.swatch-list').querySelectorAll('.configurator-swatch');
    siblings.forEach((s) => s.classList.remove('configurator-swatch--active'));
    swatch.classList.add('configurator-swatch--active');
  });
});

document.querySelectorAll('.sub-nav-pill').forEach((pill) => {
  pill.addEventListener('click', (e) => {
    e.preventDefault();
    document.querySelectorAll('.sub-nav-pill').forEach((p) => p.classList.remove('sub-nav-pill--active'));
    pill.classList.add('sub-nav-pill--active');
  });
});
