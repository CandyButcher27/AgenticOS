document.querySelectorAll('.category-tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelector('.category-tab.active')?.classList.remove('active');
    tab.classList.add('active');
  });
});

const cookieCard = document.getElementById('cookieCard');
const dismissCookie = () => cookieCard?.remove();
document.getElementById('cookieClose')?.addEventListener('click', dismissCookie);
document.getElementById('cookieAccept')?.addEventListener('click', (e) => {
  e.preventDefault();
  dismissCookie();
});

const hamburger = document.querySelector('.nav-hamburger');
const navMenu = document.querySelector('.nav-menu');
hamburger?.addEventListener('click', () => {
  navMenu.style.display = navMenu.style.display === 'flex' ? 'none' : 'flex';
  navMenu.style.flexDirection = 'column';
  navMenu.style.position = 'absolute';
  navMenu.style.top = '64px';
  navMenu.style.left = '0';
  navMenu.style.right = '0';
  navMenu.style.background = 'var(--canvas)';
  navMenu.style.padding = '16px 32px';
  navMenu.style.borderBottom = '1px solid var(--hairline)';
  navMenu.style.gap = '16px';
});
