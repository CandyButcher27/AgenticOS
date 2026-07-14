document.addEventListener('DOMContentLoaded', function() {
  // Code tab functionality
  const codeTabs = document.querySelectorAll('.code-tab');
  const codeContent = document.querySelector('.code-content code');
  
  const codeSnippets = {
    'Python': `import replicate

output = replicate.run(
  "stability-ai/stable-diffusion:latest",
  input={"prompt": "a fantasy landscape"}
)
print(output)`,
    'Node.js': `const Replicate = require('replicate');

const replicate = new Replicate({
  auth: process.env.REPLICATE_API_TOKEN
});

const output = await replicate.run(
  "stability-ai/stable-diffusion:latest",
  {input: {prompt: "a fantasy landscape"}}
);

console.log(output);`,
    'cURL': `curl -X POST https://api.replicate.com/v1/models/stability-ai/stable-diffusion/actions/run \
  -H "Authorization: Token $REPLICATE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"input": {"prompt": "a fantasy landscape"}}'`
  };
  
  codeTabs.forEach(tab => {
    tab.addEventListener('click', function() {
      // Remove active class from all tabs
      codeTabs.forEach(t => t.classList.remove('code-tab-active'));
      // Add active class to clicked tab
      this.classList.add('code-tab-active');
      
      // Update code content
      const language = this.getAttribute('data-language');
      if (codeContent && codeSnippets[language]) {
        codeContent.textContent = codeSnippets[language];
      }
    });
  });
  
  // Intersection Observer for fade-in animations
  const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
  };
  
  const observer = new IntersectionObserver(function(entries) {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = '1';
        entry.target.style.transform = 'translateY(0)';
      }
    });
  }, observerOptions);
  
  // Observe section elements for fade-in effect
  const sections = document.querySelectorAll('.section, .code-section');
  sections.forEach(section => {
    section.style.opacity = '0';
    section.style.transform = 'translateY(20px)';
    section.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    observer.observe(section);
  });
  
  // Smooth scroll for anchor links
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      e.preventDefault();
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        target.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        });
      }
    });
  });
  
  // Copy to clipboard functionality for code blocks
  const copyButtons = document.querySelectorAll('.copy-button');
  copyButtons.forEach(button => {
    button.addEventListener('click', function() {
      const codeBlock = this.closest('.code-block').querySelector('code');
      const text = codeBlock.textContent;
      
      navigator.clipboard.writeText(text).then(function() {
        const originalText = this.textContent;
        this.textContent = 'Copied!';
        setTimeout(function() {
          this.textContent = originalText;
        }.bind(this), 2000);
      }.bind(this));
    });
  });
  
  // Handle window resize for responsive adjustments
  let resizeTimer;
  window.addEventListener('resize', function() {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(function() {
      // Recalculate any layout-dependent values here
      const isMobile = window.innerWidth < 768;
      document.body.classList.toggle('mobile-view', isMobile);
    }, 250);
  });
});