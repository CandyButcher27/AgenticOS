document.querySelectorAll('.product-tab').forEach((tab) => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.product-tab').forEach((t) => {
      t.classList.remove('selected');
      t.setAttribute('aria-selected', 'false');
    });
    tab.classList.add('selected');
    tab.setAttribute('aria-selected', 'true');
  });
});

const newsletterForm = document.getElementById('newsletter-form');
if (newsletterForm) {
  newsletterForm.addEventListener('submit', (event) => {
    event.preventDefault();
    const input = newsletterForm.querySelector('.newsletter-input');
    if (input && input.value) {
      input.value = '';
      input.placeholder = 'Thanks for subscribing!';
    }
  });
}
