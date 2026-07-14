document.querySelectorAll('.faq-row').forEach((row) => {
  row.addEventListener('click', () => {
    const expanded = row.getAttribute('aria-expanded') === 'true';
    row.setAttribute('aria-expanded', String(!expanded));
    row.querySelector('.faq-row__chevron').textContent = expanded ? '＋' : '－';
  });
});

const hamburger = document.querySelector('.hamburger');
const navCenter = document.querySelector('.nav-bar-light__center');
if (hamburger && navCenter) {
  hamburger.addEventListener('click', () => {
    const expanded = hamburger.getAttribute('aria-expanded') === 'true';
    hamburger.setAttribute('aria-expanded', String(!expanded));
    navCenter.style.display = expanded ? '' : 'flex';
    navCenter.style.flexDirection = 'column';
    navCenter.style.position = 'absolute';
    navCenter.style.top = '64px';
    navCenter.style.left = '0';
    navCenter.style.right = '0';
    navCenter.style.background = '#ffffff';
    navCenter.style.padding = '20px 24px';
    navCenter.style.gap = '16px';
    navCenter.style.boxShadow = '0 8px 24px rgba(0,0,0,0.08)';
  });
}
