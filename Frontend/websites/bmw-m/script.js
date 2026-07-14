document.querySelectorAll('.category-tab, .category-tab-active').forEach((tab) => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.category-tab, .category-tab-active').forEach((t) => {
      t.classList.remove('category-tab-active');
      t.classList.add('category-tab');
    });
    tab.classList.remove('category-tab');
    tab.classList.add('category-tab-active');
  });
});

const hamburgerBtn = document.getElementById('hamburgerBtn');
const mobileMenu = document.getElementById('mobileMenu');
if (hamburgerBtn && mobileMenu) {
  hamburgerBtn.addEventListener('click', () => {
    mobileMenu.classList.toggle('is-open');
  });
  mobileMenu.querySelectorAll('a').forEach((link) => {
    link.addEventListener('click', () => mobileMenu.classList.remove('is-open'));
  });
}

const cookieCard = document.getElementById('cookieCard');
const cookieAccept = document.getElementById('cookieAccept');
const cookieDismiss = document.getElementById('cookieDismiss');
if (cookieCard) {
  [cookieAccept, cookieDismiss].forEach((btn) => {
    if (btn) {
      btn.addEventListener('click', () => cookieCard.classList.add('is-hidden'));
    }
  });
}
