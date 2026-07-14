// Together.Ai Interactive Scripts

document.addEventListener('DOMContentLoaded', () => {
  console.log("Together.Ai site template initialized.");

  // Simple CTA handler
  const primaryButtons = document.querySelectorAll('.button-primary');
  primaryButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      alert("Redirecting to the Together.Ai application platform.");
    });
  });
});
