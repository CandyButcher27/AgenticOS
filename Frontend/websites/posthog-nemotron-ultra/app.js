// PostHog Design Homage — Vanilla JS Interactions

(function() {
  'use strict';

  // DOM Elements
  const hamburger = document.querySelector('.hamburger');
  const mobileMenu = document.querySelector('.mobile-menu');
  const billingToggle = document.querySelector('#billing-toggle');
  const pricingPeriods = document.querySelectorAll('.pricing-period');
  const sidebarSections = document.querySelectorAll('.sidebar-section summary');
  const currentYear = new Date().getFullYear();

  // Mobile Navigation Toggle
  function toggleMobileMenu() {
    const isOpen = hamburger.classList.toggle('open');
    mobileMenu.classList.toggle('open', isOpen);
    hamburger.setAttribute('aria-expanded', isOpen);
    document.body.style.overflow = isOpen ? 'hidden' : '';
  }

  hamburger.addEventListener('click', toggleMobileMenu);

  // Close mobile menu on link click
  mobileMenu.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => {
      hamburger.classList.remove('open');
      mobileMenu.classList.remove('open');
      hamburger.setAttribute('aria-expanded', 'false');
      document.body.style.overflow = '';
    });
  });

  // Close mobile menu on escape
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && mobileMenu.classList.contains('open')) {
      hamburger.classList.remove('open');
      mobileMenu.classList.remove('open');
      hamburger.setAttribute('aria-expanded', 'false');
      document.body.style.overflow = '';
    }
  });

  // Billing Toggle (Monthly/Annual)
  function updatePricingDisplay() {
    const isAnnual = billingToggle.checked;
    pricingPeriods.forEach((period, index) => {
      if (index === 0) {
        period.classList.toggle('active', !isAnnual);
      } else if (index === 1) {
        period.classList.toggle('active', isAnnual);
      }
    });
    
    // Update prices
    const proPrice = document.querySelector('.pricing-tier-card.popular .price-amount');
    const proPeriod = document.querySelector('.pricing-tier-card.popular .price-period');
    const proUsage = document.querySelector('.tier-usage');
    
    if (isAnnual) {
      proPrice.textContent = '$360';
      proPeriod.textContent = '/month';
      if (proUsage) proUsage.textContent = 'Billed $4,320/year · Includes 5M events · $0.000072/event after';
    } else {
      proPrice.textContent = '$450';
      proPeriod.textContent = '/month';
      if (proUsage) proUsage.textContent = 'Includes 5M events · $0.00009/event after';
    }
  }

  billingToggle.addEventListener('change', updatePricingDisplay);

  // Sidebar Accordion
  sidebarSections.forEach(summary => {
    summary.addEventListener('click', (e) => {
      e.preventDefault();
      const section = summary.parentElement;
      const isOpen = section.classList.toggle('open');
      summary.setAttribute('aria-expanded', isOpen);
    });
  });

  // Smooth scroll for anchor links
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      const targetId = this.getAttribute('href');
      if (targetId === '#') return;
      
      const target = document.querySelector(targetId);
      if (target) {
        e.preventDefault();
        const navHeight = document.querySelector('.primary-nav').offsetHeight;
        const targetPosition = target.getBoundingClientRect().top + window.pageYOffset - navHeight;
        
        window.scrollTo({
          top: targetPosition,
          behavior: 'smooth'
        });
      }
    });
  });

  // Intersection Observer for scroll animations
  const observerOptions = {
    root: null,
    rootMargin: '0px 0px -10% 0px',
    threshold: 0.1
  };

  const sectionObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.animationPlayState = 'running';
      }
    });
  }, observerOptions);

  document.querySelectorAll('.section').forEach(section => {
    section.style.animationPlayState = 'paused';
    sectionObserver.observe(section);
  });

  // CTA Form Handler
  const ctaForm = document.querySelector('.cta-form');
  if (ctaForm) {
    ctaForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const emailInput = ctaForm.querySelector('input[type="email"]');
      const email = emailInput.value.trim();
      
      if (email && email.includes('@')) {
        // Simulate successful submission
        const submitBtn = ctaForm.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'Welcome! Redirecting...';
        submitBtn.disabled = true;
        submitBtn.style.backgroundColor = 'var(--color-accent-green)';
        
        setTimeout(() => {
          submitBtn.textContent = originalText;
          submitBtn.disabled = false;
          submitBtn.style.backgroundColor = '';
          emailInput.value = '';
        }, 2000);
      }
    });
  }

  // Keyboard navigation for sidebar
  document.querySelectorAll('.sidebar-link').forEach(link => {
    link.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        link.click();
      }
    });
  });

  // Update copyright year
  const copyright = document.querySelector('.copyright');
  if (copyright) {
    copyright.textContent = copyright.textContent.replace('2024', currentYear);
  }

  // Parallax effect for hero hedgehog (subtle)
  const heroHedgehog = document.querySelector('.hedgehog-hero');
  if (heroHedgehog) {
    window.addEventListener('scroll', () => {
      const scrolled = window.pageYOffset;
      const rate = scrolled * 0.1;
      if (rate < 100) {
        heroHedgehog.style.transform = `translateY(${rate}px)`;
      }
    }, { passive: true });
  }

  // Active nav link highlighting on scroll
  const sections = document.querySelectorAll('section[id]');
  const navLinks = document.querySelectorAll('.nav-link, .mobile-nav-link');
  
  function highlightNavLink() {
    const scrollPos = window.pageYOffset + document.querySelector('.primary-nav').offsetHeight + 100;
    
    sections.forEach(section => {
      const sectionTop = section.offsetTop;
      const sectionHeight = section.offsetHeight;
      const sectionId = section.getAttribute('id');
      
      if (scrollPos >= sectionTop && scrollPos < sectionTop + sectionHeight) {
        navLinks.forEach(link => {
          link.classList.toggle('active', link.getAttribute('href') === `#${sectionId}`);
        });
      }
    });
  }

  window.addEventListener('scroll', highlightNavLink, { passive: true });

  // Initialize
  updatePricingDisplay();
  
  // Reduce motion preference
  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  if (prefersReducedMotion.matches) {
    document.documentElement.style.setProperty('--animation-duration', '0s');
    heroHedgehog && (heroHedgehog.style.transform = 'none');
  }

  console.log('PostHog Design Homage initialized 🦔');
})();