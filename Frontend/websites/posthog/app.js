// Posthog Interactive Scripts

document.addEventListener('DOMContentLoaded', () => {
  console.log("Posthog site template initialized.");

  // Simple CTA handler
  const primaryButtons = document.querySelectorAll('.button-primary-pressed');
  primaryButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      alert("Redirecting to the Posthog application platform.");
    });
  });
});
