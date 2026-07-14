document.querySelectorAll('.faq-row').forEach((row) => {
  row.addEventListener('click', () => {
    const expanded = row.getAttribute('aria-expanded') === 'true';
    row.setAttribute('aria-expanded', String(!expanded));
    row.querySelector('.faq-row__chevron').textContent = expanded ? '+' : '−';
  });
});

const pauseBtn = document.querySelector('.hero__pause');
if (pauseBtn) {
  let playing = true;
  pauseBtn.addEventListener('click', () => {
    playing = !playing;
    pauseBtn.setAttribute('aria-label', playing ? 'Pause video' : 'Play video');
  });
}

const newsletterForm = document.querySelector('.newsletter-form');
if (newsletterForm) {
  newsletterForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const input = newsletterForm.querySelector('input');
    if (input.value) {
      input.value = '';
      input.placeholder = 'Subscribed!';
    }
  });
}
