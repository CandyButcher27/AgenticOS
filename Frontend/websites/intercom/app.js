document.addEventListener("DOMContentLoaded", () => {
  const nav = document.querySelector(".top-nav");
  const navToggle = document.querySelector(".nav-toggle");
  const faqButtons = document.querySelectorAll(".faq-trigger");

  if (nav && navToggle) {
    navToggle.addEventListener("click", () => {
      const isOpen = nav.classList.toggle("is-open");
      navToggle.setAttribute("aria-expanded", String(isOpen));
    });
  }

  faqButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const expanded = button.getAttribute("aria-expanded") === "true";
      const content = button.nextElementSibling;

      button.setAttribute("aria-expanded", String(!expanded));
      if (content) {
        content.hidden = expanded;
      }

      const icon = button.querySelector(".faq-icon");
      if (icon) {
        icon.textContent = expanded ? "+" : "-";
      }
    });
  });
});
