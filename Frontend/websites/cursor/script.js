// Cycle the hero agent-timeline pills to simulate live agent activity
const heroTimeline = document.querySelector('.ide-chat .timeline');
if (heroTimeline) {
  const pills = Array.from(heroTimeline.children);
  let active = pills.length - 1;

  setInterval(() => {
    pills.forEach((pill) => (pill.style.opacity = '0.35'));
    active = (active + 1) % pills.length;
    pills[active].style.opacity = '1';
  }, 1400);
}

// Mobile nav toggle reveals the primary links stacked beneath the header
const navToggle = document.querySelector('.nav-toggle');
const navCenter = document.querySelector('.top-nav__center');
if (navToggle && navCenter) {
  navToggle.addEventListener('click', () => {
    const isOpen = navCenter.classList.toggle('top-nav__center--open');
    navCenter.style.display = isOpen ? 'flex' : 'none';
    navCenter.style.position = 'absolute';
    navCenter.style.top = '64px';
    navCenter.style.left = '0';
    navCenter.style.right = '0';
    navCenter.style.flexDirection = 'column';
    navCenter.style.background = 'var(--canvas)';
    navCenter.style.padding = '16px 32px';
    navCenter.style.borderBottom = '1px solid var(--hairline)';
    navCenter.style.gap = '16px';
  });
}

// Highlight the pricing tier featured card slightly on hover for tactile feedback
document.querySelectorAll('.pricing-tier-card, .pricing-tier-featured').forEach((card) => {
  card.addEventListener('mouseenter', () => {
    card.style.borderColor = 'var(--hairline-strong)';
  });
  card.addEventListener('mouseleave', () => {
    card.style.borderColor = '';
  });
});
