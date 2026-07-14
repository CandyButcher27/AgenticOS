document.querySelectorAll('.faq-row').forEach((row) => {
  row.addEventListener('click', () => {
    const expanded = row.getAttribute('aria-expanded') === 'true';
    document.querySelectorAll('.faq-row').forEach((r) => {
      r.setAttribute('aria-expanded', 'false');
      r.querySelector('.faq-row__chevron').textContent = '+';
    });
    if (!expanded) {
      row.setAttribute('aria-expanded', 'true');
      row.querySelector('.faq-row__chevron').textContent = '−';
    }
  });
});

document.querySelectorAll('.nav-pill-group .category-tab').forEach((tab) => {
  tab.addEventListener('click', () => {
    tab.closest('.nav-pill-group').querySelectorAll('.category-tab').forEach((t) => {
      t.classList.remove('category-tab--active');
      t.setAttribute('aria-selected', 'false');
    });
    tab.classList.add('category-tab--active');
    tab.setAttribute('aria-selected', 'true');
  });
});

document.querySelectorAll('.time-slot').forEach((slot) => {
  slot.addEventListener('click', () => {
    slot.closest('.mockup__slots').querySelectorAll('.time-slot').forEach((s) => {
      s.classList.remove('time-slot--active');
    });
    slot.classList.add('time-slot--active');
  });
});

const navToggle = document.querySelector('.nav-toggle');
const topNavCenter = document.querySelector('.top-nav__center');
if (navToggle && topNavCenter) {
  navToggle.addEventListener('click', () => {
    const expanded = navToggle.getAttribute('aria-expanded') === 'true';
    navToggle.setAttribute('aria-expanded', String(!expanded));
    topNavCenter.style.display = expanded ? 'none' : 'flex';
  });
}
