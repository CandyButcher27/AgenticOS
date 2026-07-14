// Supabase Interactive Scripts

document.addEventListener('DOMContentLoaded', () => {
  console.log("Supabase site template initialized.");

  // Simple CTA handler
  const primaryButtons = document.querySelectorAll('.button-primary-green-pressed');
  primaryButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      alert("Redirecting to the Supabase application platform.");
    });
  });
});
