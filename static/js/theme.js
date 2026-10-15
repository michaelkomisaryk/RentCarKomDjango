(function () {
  const root = document.documentElement;
  const toggle = document.querySelector("[data-theme-toggle]");
  const menu = document.querySelector("[data-menu]");
  const nav = document.querySelector("[data-nav]");

  function apply(theme) {
    root.setAttribute("data-theme", theme);
    localStorage.setItem("rck-theme", theme);
    if (toggle) {
      toggle.setAttribute("aria-pressed", theme === "dark" ? "true" : "false");
    }
  }

  if (toggle) {
    toggle.setAttribute("aria-pressed", root.getAttribute("data-theme") === "dark" ? "true" : "false");
  }

  toggle?.addEventListener("click", function () {
    apply(root.getAttribute("data-theme") === "dark" ? "light" : "dark");
  });

  menu?.addEventListener("click", function () {
    const open = nav.classList.toggle("is-open");
    menu.setAttribute("aria-expanded", open ? "true" : "false");
  });
})();
