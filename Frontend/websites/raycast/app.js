const menuButton = document.querySelector(".menu-toggle");
const menu = document.querySelector(".site-menu");
const paletteRows = document.querySelectorAll(".palette-row");

if (menuButton && menu) {
  menuButton.addEventListener("click", () => {
    const expanded = menuButton.getAttribute("aria-expanded") === "true";
    menuButton.setAttribute("aria-expanded", String(!expanded));
    menu.classList.toggle("is-open", !expanded);
  });
}

paletteRows.forEach((row) => {
  row.addEventListener("click", () => {
    paletteRows.forEach((item) => item.classList.remove("is-active"));
    row.classList.add("is-active");
  });
});
