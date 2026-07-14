document.getElementById('menuToggle').addEventListener('click', () => {
  document.getElementById('navBar').classList.toggle('nav-bar--open');
});

const newsletterForm = document.getElementById('newsletterForm');
const newsletterNote = document.getElementById('newsletterNote');
newsletterForm.addEventListener('submit', (e) => {
  e.preventDefault();
  const email = newsletterForm.querySelector('input').value;
  newsletterNote.textContent = email ? `Thanks — we'll send WIRED Daily to ${email}.` : '';
  newsletterForm.reset();
});
