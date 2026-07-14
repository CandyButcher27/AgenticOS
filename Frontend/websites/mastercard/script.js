// Mobile hamburger toggles the nav links open as a stacked overlay list
const hamburger = document.querySelector('.nav-hamburger');
const navLinks = document.querySelector('.nav-links');
if (hamburger && navLinks) {
  hamburger.addEventListener('click', () => {
    navLinks.classList.toggle('nav-links--open');
  });
}

// Newsletter form
const newsletterForm = document.getElementById('newsletter-form');
const newsletterNote = document.getElementById('newsletter-note');
if (newsletterForm) {
  newsletterForm.addEventListener('submit', (e) => {
    e.preventDefault();
    newsletterNote.textContent = "You're subscribed. Thanks for staying in the loop.";
    newsletterForm.reset();
  });
}

// Cookie consent bar
const consentBar = document.getElementById('consent-bar');
const consentAccept = document.getElementById('consent-accept');
const consentDetails = document.getElementById('consent-details');

function hideConsentBar() {
  if (consentBar) consentBar.classList.add('consent-bar--hidden');
}

if (consentAccept) consentAccept.addEventListener('click', hideConsentBar);
if (consentDetails) consentDetails.addEventListener('click', hideConsentBar);

// Play button toggles a simple pressed state (no real video source available)
const playBtn = document.querySelector('.play-btn');
if (playBtn) {
  playBtn.addEventListener('click', () => {
    playBtn.classList.toggle('play-btn--playing');
  });
}
