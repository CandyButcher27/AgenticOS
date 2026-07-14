document.querySelectorAll('.faq-row').forEach((row) => {
  row.addEventListener('click', () => {
    const expanded = row.getAttribute('aria-expanded') === 'true';
    row.setAttribute('aria-expanded', String(!expanded));
    row.querySelector('.faq-row__chevron').textContent = expanded ? '+' : '−';
  });
});

document.querySelectorAll('.pill-tab').forEach((tab) => {
  tab.addEventListener('click', () => {
    tab.closest('.pill-tabs').querySelectorAll('.pill-tab').forEach((t) => t.classList.remove('pill-tab--active'));
    tab.classList.add('pill-tab--active');
  });
});
