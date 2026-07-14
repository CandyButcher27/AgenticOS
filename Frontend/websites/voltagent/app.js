// Voltagent Interactive Scripts

document.addEventListener('DOMContentLoaded', () => {
  console.log("Voltagent site template initialized.");

  // Simple CTA handler
  const primaryButtons = document.querySelectorAll('.button-primary');
  primaryButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      alert("Redirecting to the Voltagent application platform.");
    });
  });
});
