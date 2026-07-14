const stickyBar = document.getElementById('stickyBar');
const heroSection = document.querySelector('.hero');

if (stickyBar && heroSection) {
  const observer = new IntersectionObserver(
    ([entry]) => {
      stickyBar.classList.toggle('visible', !entry.isIntersecting);
    },
    { threshold: 0 }
  );
  observer.observe(heroSection);
}

const chips = document.querySelectorAll('.chip');
chips.forEach((chip) => {
  chip.addEventListener('click', () => {
    chips.forEach((c) => c.classList.remove('chip--selected'));
    chip.classList.add('chip--selected');
  });
});

const hamburger = document.querySelector('.hamburger');
const globalNavLinks = document.querySelector('.global-nav__links');
if (hamburger && globalNavLinks) {
  hamburger.addEventListener('click', () => {
    globalNavLinks.classList.toggle('open');
  });
}
