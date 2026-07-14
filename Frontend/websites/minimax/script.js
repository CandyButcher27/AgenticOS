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

document.querySelectorAll('.product-card').forEach((card) => {
  card.addEventListener('mouseenter', () => card.style.transform = 'translateY(-4px)');
  card.addEventListener('mouseleave', () => card.style.transform = 'translateY(0)');
  card.style.transition = 'transform 0.2s ease';
});
