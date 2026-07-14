document.addEventListener('DOMContentLoaded', function() {
  const hamburger = document.querySelector('.hamburger');
  const navLinks = document.querySelector('.nav-links');

  hamburger.addEventListener('click', function() {
    navLinks.classList.toggle('active');
  });

  const codeTabs = document.querySelectorAll('.code-tab');
  
  codeTabs.forEach(tab => {
    tab.addEventListener('click', function() {
      document.querySelector('.code-tab.active').classList.remove('active');
      this.classList.add('active');
    });
  });
});