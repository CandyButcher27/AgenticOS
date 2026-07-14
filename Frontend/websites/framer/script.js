// Mobile nav toggle
const navToggle = document.getElementById('navToggle');
const mobileNav = document.getElementById('mobileNav');

if (navToggle && mobileNav) {
  navToggle.addEventListener('click', () => {
    const isOpen = mobileNav.classList.toggle('open');
    navToggle.setAttribute('aria-expanded', String(isOpen));
  });

  mobileNav.querySelectorAll('a').forEach((link) => {
    link.addEventListener('click', () => {
      mobileNav.classList.remove('open');
      navToggle.setAttribute('aria-expanded', 'false');
    });
  });
}

// Pricing period toggle
const pricingTabs = document.querySelectorAll('.pricing-tab');
const priceValues = document.querySelectorAll('.price__value');

pricingTabs.forEach((tab) => {
  tab.addEventListener('click', () => {
    pricingTabs.forEach((t) => {
      t.classList.remove('pricing-tab--selected');
      t.setAttribute('aria-selected', 'false');
    });
    tab.classList.add('pricing-tab--selected');
    tab.setAttribute('aria-selected', 'true');

    const period = tab.dataset.period;
    priceValues.forEach((el) => {
      const value = period === 'yearly' ? el.dataset.yearly : el.dataset.monthly;
      if (value) el.textContent = value;
    });
  });
});

// FAQ accordion
document.querySelectorAll('.faq-row').forEach((row) => {
  const question = row.querySelector('.faq-row__question');
  question.addEventListener('click', () => {
    const isOpen = row.getAttribute('data-open') === 'true';
    document.querySelectorAll('.faq-row').forEach((r) => r.removeAttribute('data-open'));
    if (!isOpen) row.setAttribute('data-open', 'true');
  });
});
