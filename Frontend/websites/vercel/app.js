// Vercel Interactive Scripts

document.addEventListener('DOMContentLoaded', () => {
  console.log("Vercel site template initialized.");

  // Simple CTA handler
  const primaryButtons = document.querySelectorAll('.button-primary-sm');
  primaryButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      alert("Redirecting to the Vercel application platform.");
    });
  });
});
