const menuButton = document.querySelector(".menu-toggle");
const menu = document.querySelector(".site-menu");
const tabs = document.querySelectorAll(".tab");
const faqRows = document.querySelectorAll(".faq-row");

if (menuButton && menu) {
  menuButton.addEventListener("click", () => {
    const expanded = menuButton.getAttribute("aria-expanded") === "true";
    menuButton.setAttribute("aria-expanded", String(!expanded));
    menu.classList.toggle("is-open", !expanded);
  });
}

tabs.forEach((tab) => {
  tab.addEventListener("click", () => {
    tabs.forEach((item) => item.classList.remove("is-active"));
    tab.classList.add("is-active");
  });
});

faqRows.forEach((row) => {
  row.addEventListener("click", () => {
    faqRows.forEach((item) => item.classList.remove("is-open"));
    row.classList.add("is-open");
  });
});
