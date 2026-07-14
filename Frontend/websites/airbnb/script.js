document.querySelectorAll('.category-tab').forEach((tab) => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.category-tab').forEach((t) => t.classList.remove('category-tab--active'));
    tab.classList.add('category-tab--active');
  });
});

document.querySelectorAll('.heart-button').forEach((btn) => {
  btn.addEventListener('click', (e) => {
    e.preventDefault();
    btn.classList.toggle('heart-button--active');
    const svg = btn.querySelector('svg');
    if (btn.classList.contains('heart-button--active')) {
      svg.setAttribute('fill', 'currentColor');
      svg.setAttribute('stroke', 'none');
    } else {
      svg.setAttribute('fill', 'none');
      svg.setAttribute('stroke', 'currentColor');
    }
  });
});

document.querySelectorAll('.product-tab').forEach((tab) => {
  tab.addEventListener('click', (e) => {
    e.preventDefault();
    document.querySelectorAll('.product-tab').forEach((t) => {
      t.classList.remove('product-tab--active');
      t.classList.add('product-tab--inactive');
    });
    tab.classList.add('product-tab--active');
    tab.classList.remove('product-tab--inactive');
  });
});
