document.addEventListener('DOMContentLoaded', () => {

  // Hamburger menu toggle (mobile nav)
  const hamburger = document.querySelector('.hamburger');
  const navLinks = document.querySelector('.nav-bar__links');

  if (hamburger && navLinks) {
    hamburger.addEventListener('click', () => {
      const isOpen = navLinks.classList.toggle('nav-bar__links--open');
      navLinks.style.display = isOpen ? 'flex' : '';
      hamburger.classList.toggle('hamburger--active', isOpen);
    });
  }

  // Hero play button — placeholder interaction
  const playBtn = document.querySelector('.hero-band-dark__play');
  if (playBtn) {
    playBtn.addEventListener('click', () => {
      const icon = playBtn.querySelector('svg path');
      const isPlaying = playBtn.classList.toggle('is-playing');
      if (icon) {
        icon.setAttribute('d', isPlaying
          ? 'M7 5h4v14H7zM13 5h4v14h-4z'
          : 'M8 5v14l11-7z');
      }
    });
  }

  // Smooth scroll for in-page anchor links
  document.querySelectorAll('a[href^="#"]').forEach((link) => {
    link.addEventListener('click', (e) => {
      const targetId = link.getAttribute('href');
      if (targetId.length > 1) {
        const target = document.querySelector(targetId);
        if (target) {
          e.preventDefault();
          target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      }
    });
  });

  // Newsletter signup form
  const form = document.getElementById('signup-form');
  const message = document.getElementById('form-message');

  if (form && message) {
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const input = form.querySelector('input[type="email"]');
      const email = input ? input.value.trim() : '';
      const isValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);

      if (isValid) {
        message.textContent = `Thanks — we'll send offers to ${email}.`;
        form.reset();
      } else {
        message.textContent = 'Please enter a valid email address.';
      }
    });
  }

  // Sticky nav shadow on scroll
  const navBar = document.querySelector('.nav-bar');
  if (navBar) {
    window.addEventListener('scroll', () => {
      navBar.classList.toggle('nav-bar--scrolled', window.scrollY > 8);
    });
  }
});
