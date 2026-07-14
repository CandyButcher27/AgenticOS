document.querySelectorAll('.faq-row').forEach((row) => {
  row.addEventListener('click', () => {
    const expanded = row.getAttribute('aria-expanded') === 'true';
    row.setAttribute('aria-expanded', String(!expanded));
    row.querySelector('.faq-row__chevron').textContent = expanded ? '+' : '−';
  });
});

document.querySelectorAll('.app-shell-item').forEach((item) => {
  item.addEventListener('click', () => {
    document.querySelectorAll('.app-shell-item').forEach((i) => i.classList.remove('app-shell-item--active'));
    item.classList.add('app-shell-item--active');
  });
});
