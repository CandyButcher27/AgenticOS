const menuButton = document.querySelector(".menu-toggle");
const menu = document.querySelector(".site-menu");
const thumbs = document.querySelectorAll(".thumb");
const swatches = document.querySelectorAll(".swatch");
const radioCards = document.querySelectorAll(".radio-card");

if (menuButton && menu) {
  menuButton.addEventListener("click", () => {
    const expanded = menuButton.getAttribute("aria-expanded") === "true";
    menuButton.setAttribute("aria-expanded", String(!expanded));
    menu.classList.toggle("is-open", !expanded);
  });
}

thumbs.forEach((thumb) => {
  thumb.addEventListener("click", () => {
    thumbs.forEach((item) => item.classList.remove("is-active"));
    thumb.classList.add("is-active");
  });
});

swatches.forEach((swatch) => {
  swatch.addEventListener("click", () => {
    swatches.forEach((item) => item.classList.remove("is-selected"));
    swatch.classList.add("is-selected");
  });
});

radioCards.forEach((card) => {
  card.addEventListener("click", () => {
    radioCards.forEach((item) => item.classList.remove("is-selected"));
    card.classList.add("is-selected");
  });
});
