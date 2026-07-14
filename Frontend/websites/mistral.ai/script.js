document.querySelectorAll('.faq-accordion-item').forEach((item) => {
  const question = item.querySelector('.faq-accordion-item__q');
  question.addEventListener('click', () => {
    const expanded = item.getAttribute('aria-expanded') === 'true';
    item.setAttribute('aria-expanded', String(!expanded));
    item.querySelector('.faq-accordion-item__chevron').textContent = expanded ? '＋' : '－';
  });
});
