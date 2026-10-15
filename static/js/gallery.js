(function () {
  const gallery = document.querySelector("[data-gallery]");
  if (!gallery) return;

  const sourceNode = gallery.querySelector("[data-sources]");
  const sources = sourceNode ? JSON.parse(sourceNode.textContent) : [];
  if (!sources.length) return;

  const hero = gallery.querySelector(".hero");
  const lightbox = gallery.querySelector("[data-lightbox]");
  const lightboxImg = lightbox.querySelector(".lightbox-photo");
  const thumbs = [...gallery.querySelectorAll(".thumb-btn")];
  let index = 0;

  function show(next) {
    index = (next + sources.length) % sources.length;
    hero.src = sources[index];
    lightboxImg.src = sources[index];
    gallery.querySelectorAll("[data-index]").forEach((node) => {
      node.textContent = String(index + 1);
    });
    thumbs.forEach((button, i) => {
      button.classList.toggle("is-active", i === index);
    });
  }

  function openLightbox() {
    lightbox.hidden = false;
    document.body.classList.add("lightbox-open");
    lightboxImg.src = sources[index];
  }

  function closeLightbox() {
    lightbox.hidden = true;
    document.body.classList.remove("lightbox-open");
  }

  gallery.addEventListener("click", (event) => {
    const arrow = event.target.closest("[data-dir]");
    if (arrow) {
      show(index + Number(arrow.dataset.dir));
      return;
    }
    const thumb = event.target.closest(".thumb-btn");
    if (thumb) {
      show(thumbs.indexOf(thumb));
      return;
    }
    if (event.target.closest("[data-fullscreen]")) {
      openLightbox();
    }
  });

  lightbox.querySelector("[data-close]").addEventListener("click", closeLightbox);
  lightbox.addEventListener("click", (event) => {
    if (event.target === lightbox) closeLightbox();
  });

  document.addEventListener("keydown", (event) => {
    const typing = event.target.closest("input, textarea, select");
    if (event.key === "Escape" && !lightbox.hidden) {
      closeLightbox();
      return;
    }
    if (typing || sources.length < 2) return;
    if (event.key === "ArrowLeft") show(index - 1);
    if (event.key === "ArrowRight") show(index + 1);
  });
})();
