document.addEventListener('DOMContentLoaded', () => {

  // Mobile hamburger drawer
  const hamburgerBtn = document.getElementById('hamburgerBtn');
  const mobileDrawer = document.getElementById('mobileDrawer');
  if (hamburgerBtn && mobileDrawer) {
    hamburgerBtn.addEventListener('click', () => {
      mobileDrawer.classList.toggle('open');
    });
  }

  // FAQ accordion
  document.querySelectorAll('.faq-item__question').forEach((btn) => {
    btn.addEventListener('click', () => {
      const item = btn.closest('.faq-item');
      const isOpen = item.classList.contains('open');
      document.querySelectorAll('.faq-item.open').forEach((openItem) => {
        openItem.classList.remove('open');
        openItem.querySelector('.faq-item__question').setAttribute('aria-expanded', 'false');
      });
      if (!isOpen) {
        item.classList.add('open');
        btn.setAttribute('aria-expanded', 'true');
      }
    });
  });
  // Open first FAQ item by default
  const firstFaq = document.querySelector('.faq-item');
  if (firstFaq) firstFaq.classList.add('open');

  // Pricing/Roadmap pill tabs
  document.querySelectorAll('.pill-tabs .pill-tab').forEach((tab) => {
    tab.addEventListener('click', () => {
      document.querySelectorAll('.pill-tabs .pill-tab').forEach((t) => t.classList.remove('pill-tab--active'));
      tab.classList.add('pill-tab--active');
    });
  });

  // Monthly/Annual toggle
  document.querySelectorAll('.toggle-monthly-yearly .toggle-thumb').forEach((thumb) => {
    thumb.addEventListener('click', () => {
      document.querySelectorAll('.toggle-monthly-yearly .toggle-thumb').forEach((t) => t.classList.remove('toggle-thumb--active'));
      thumb.classList.add('toggle-thumb--active');
    });
  });

  // Docs segmented tabs
  document.querySelectorAll('.segmented-tab').forEach((tab) => {
    tab.addEventListener('click', () => {
      document.querySelectorAll('.segmented-tab').forEach((t) => t.classList.remove('segmented-tab--active'));
      tab.classList.add('segmented-tab--active');
    });
  });

});
