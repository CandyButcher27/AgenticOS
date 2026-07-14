document.querySelectorAll('.faq-row').forEach((row) => {
  row.addEventListener('click', () => {
    const expanded = row.getAttribute('aria-expanded') === 'true';
    row.setAttribute('aria-expanded', String(!expanded));
    row.querySelector('.faq-row__chevron').textContent = expanded ? '＋' : '－';
  });
});

document.querySelectorAll('.swatch-dot').forEach((dot) => {
  dot.addEventListener('click', () => {
    const siblings = dot.closest('.product-card__swatches').querySelectorAll('.swatch-dot');
    siblings.forEach((s) => s.classList.remove('swatch-dot--active'));
    dot.classList.add('swatch-dot--active');
  });
});
