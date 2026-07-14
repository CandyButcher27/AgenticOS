document.querySelectorAll('.faq-row').forEach((row) => {
  const btn = row.querySelector('.faq-row__q');
  btn.addEventListener('click', () => {
    const expanded = row.getAttribute('aria-expanded') === 'true';
    row.setAttribute('aria-expanded', String(!expanded));
    row.querySelector('.faq-row__chevron').textContent = expanded ? '＋' : '－';
  });
});

document.querySelectorAll('.newsletter').forEach((form) => {
  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const input = form.querySelector('.text-input');
    const btn = form.querySelector('button');
    if (input && input.value) {
      btn.textContent = 'Thanks — check your inbox!';
      input.value = '';
    }
  });
});
