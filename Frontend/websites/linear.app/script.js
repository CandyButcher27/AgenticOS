const navToggle = document.querySelector('.nav-toggle');
const mobileNav = document.querySelector('.top-nav__mobile');

if (navToggle && mobileNav) {
  navToggle.addEventListener('click', () => {
    const expanded = navToggle.getAttribute('aria-expanded') === 'true';
    navToggle.setAttribute('aria-expanded', String(!expanded));
    mobileNav.classList.toggle('is-open', !expanded);
  });
}

document.querySelectorAll('.pricing-tab-default, .pricing-tab-selected').forEach((tab) => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.pricing-tabs button').forEach((btn) => {
      btn.classList.remove('pricing-tab-selected');
      btn.classList.add('pricing-tab-default');
    });
    tab.classList.remove('pricing-tab-default');
    tab.classList.add('pricing-tab-selected');
  });
});
