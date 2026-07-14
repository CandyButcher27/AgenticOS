document.querySelectorAll('.console-showcase__thumb').forEach((thumb) => {
  thumb.addEventListener('click', () => {
    document.querySelectorAll('.console-showcase__thumb').forEach((t) =>
      t.classList.remove('console-showcase__thumb--active')
    );
    thumb.classList.add('console-showcase__thumb--active');
  });
});

document.querySelectorAll('.pagination-dot').forEach((dot, index, dots) => {
  dot.addEventListener('click', () => {
    dots.forEach((d) => d.classList.remove('pagination-dot--active'));
    dot.classList.add('pagination-dot--active');
  });
});

document.querySelectorAll('.carousel-controls').forEach((controls) => {
  const rail = controls.closest('.section__heading-row').parentElement.querySelector('.game-tile-rail');
  const [prev, next] = controls.querySelectorAll('.carousel-paddle');
  const scrollAmount = 320;
  prev.addEventListener('click', () => rail.scrollBy({ left: -scrollAmount, behavior: 'smooth' }));
  next.addEventListener('click', () => rail.scrollBy({ left: scrollAmount, behavior: 'smooth' }));
});
