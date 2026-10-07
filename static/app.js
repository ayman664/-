document.querySelectorAll("[data-open-dialog]").forEach((button) => {
  const dialog = document.querySelector(button.dataset.openDialog);
  if (dialog) button.addEventListener("click", () => dialog.showModal());
});

document.querySelectorAll("[data-close-dialog]").forEach((button) => {
  const dialog = button.closest("dialog");
  if (dialog) button.addEventListener("click", () => dialog.close());
});

document.querySelectorAll("dialog").forEach((dialog) => {
  dialog.addEventListener("click", (event) => {
    if (event.target === dialog) dialog.close();
  });
});

const filterButtons = document.querySelectorAll(".filter");
const poemCards = document.querySelectorAll(".poem-card");
const poemBodies = document.querySelectorAll(".poem-body-item");
const emptyPoetryMessage = document.querySelector("[data-poem-empty]");
let poetrySelection = poemCards[0] || null;

const updatePoetrySelection = (selectedFilter, selectedCard = null) => {
  const eligibleCards = Array.from(poemCards).filter((card) => {
    return card.dataset.category === selectedFilter;
  });

  const cardToActivate = selectedCard && selectedCard.dataset.category === selectedFilter
    ? selectedCard
    : eligibleCards[0] || null;

  poemCards.forEach((card) => {
    const visible = card.dataset.category === selectedFilter;
    card.style.display = visible ? "block" : "none";
    card.classList.toggle("is-active", card === cardToActivate);
    card.setAttribute("aria-pressed", String(card === cardToActivate));
  });

  poemBodies.forEach((body) => {
    body.classList.toggle("is-active", cardToActivate !== null && body.id === cardToActivate.dataset.target);
  });
  if (emptyPoetryMessage) emptyPoetryMessage.hidden = eligibleCards.length > 0;
};

filterButtons.forEach((button) => {
  button.addEventListener("click", () => {
    filterButtons.forEach((item) => item.classList.toggle("is-active", item === button));
    updatePoetrySelection(button.dataset.filter);
  });
});

poemCards.forEach((card) => {
  card.addEventListener("click", () => {
    poetrySelection = card;
    updatePoetrySelection(document.querySelector(".filter.is-active")?.dataset.filter || "شعر", card);
  });
});

updatePoetrySelection(document.querySelector(".filter.is-active")?.dataset.filter || "شعر", poetrySelection);

const gallery = document.querySelector("[data-gallery]");
if (gallery) {
  const slides = Array.from(gallery.querySelectorAll("[data-gallery-slide]"));
  const dots = Array.from(gallery.querySelectorAll("[data-gallery-dot]"));
  const counter = gallery.querySelector("[data-gallery-counter]");
  let activeSlide = 0;
  let autoplayTimer = null;
  const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

  const showSlide = (index) => {
    activeSlide = (index + slides.length) % slides.length;
    slides.forEach((slide, slideIndex) => {
      const isActive = slideIndex === activeSlide;
      slide.classList.toggle("is-active", isActive);
      slide.setAttribute("aria-hidden", String(!isActive));
    });
    dots.forEach((dot, dotIndex) => {
      const isActive = dotIndex === activeSlide;
      dot.classList.toggle("is-active", isActive);
      dot.setAttribute("aria-pressed", String(isActive));
    });
    if (counter) counter.textContent = `${activeSlide + 1} / ${slides.length}`;
  };

  const stopAutoplay = () => {
    if (autoplayTimer !== null) {
      window.clearInterval(autoplayTimer);
      autoplayTimer = null;
    }
  };

  const startAutoplay = () => {
    stopAutoplay();
    if (!prefersReducedMotion.matches && !document.hidden && !gallery.matches(":hover") && !gallery.contains(document.activeElement)) {
      autoplayTimer = window.setInterval(() => showSlide(activeSlide + 1), 5000);
    }
  };

  gallery.querySelector("[data-gallery-previous]")?.addEventListener("click", () => {
    showSlide(activeSlide - 1);
    startAutoplay();
  });
  gallery.querySelector("[data-gallery-next]")?.addEventListener("click", () => {
    showSlide(activeSlide + 1);
    startAutoplay();
  });
  dots.forEach((dot) => {
    dot.addEventListener("click", () => {
      showSlide(Number(dot.dataset.galleryDot));
      startAutoplay();
    });
  });
  gallery.addEventListener("keydown", (event) => {
    if (event.key === "ArrowLeft") {
      showSlide(activeSlide + 1);
      startAutoplay();
    }
    if (event.key === "ArrowRight") {
      showSlide(activeSlide - 1);
      startAutoplay();
    }
  });
  gallery.addEventListener("mouseenter", stopAutoplay);
  gallery.addEventListener("mouseleave", startAutoplay);
  gallery.addEventListener("focusin", stopAutoplay);
  gallery.addEventListener("focusout", startAutoplay);
  document.addEventListener("visibilitychange", startAutoplay);
  prefersReducedMotion.addEventListener("change", startAutoplay);
  startAutoplay();
}