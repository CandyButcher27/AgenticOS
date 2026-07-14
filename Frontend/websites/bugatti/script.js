// Mobile menu toggle (hamburger acts as a no-op placeholder for a future drawer)
const menuBtn = document.querySelector('.nav-link--menu');
if (menuBtn) {
  menuBtn.addEventListener('click', () => {
    document.body.classList.toggle('nav-open');
  });
}

// Fade sections in as they enter the viewport
const revealTargets = document.querySelectorAll('.section, .hero-photo-band, .cta-band-photo');
revealTargets.forEach((el) => {
  el.style.opacity = '0';
  el.style.transform = 'translateY(16px)';
  el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
});

const observer = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      entry.target.style.opacity = '1';
      entry.target.style.transform = 'translateY(0)';
      observer.unobserve(entry.target);
    }
  });
}, { threshold: 0.1 });

revealTargets.forEach((el) => observer.observe(el));
