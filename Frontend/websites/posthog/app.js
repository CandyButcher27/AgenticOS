document.addEventListener('DOMContentLoaded', function() {
    const navLinks = document.querySelectorAll('.nav-link');
    const buttons = document.querySelectorAll('.button-primary, .button-secondary');
    
    navLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const href = this.getAttribute('href');
            if (href !== '#' && href !== 'javascript:void(0)') {
                window.location.href = href;
            }
        });
    });
    
    buttons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            const buttonText = this.textContent.trim();
            if (buttonText.includes('Get started') || buttonText.includes('Try it free')) {
                const event = new CustomEvent('ctaClick', {
                    detail: { action: buttonText }
                });
                document.dispatchEvent(event);
            }
        });
    });
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(function(entry) {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, {
        threshold: 0.1
    });
    
    const animatedElements = document.querySelectorAll('.feature-tile, .pricing-tier-card');
    animatedElements.forEach(function(el) {
        observer.observe(el);
    });
    
    window.addEventListener('resize', function() {
        const nav = document.querySelector('.primary-nav');
        if (window.innerWidth <= 768) {
            nav.style.position = 'relative';
        } else {
            nav.style.position = 'sticky';
        }
    });
});