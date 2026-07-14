const voices = [
  {
    category: "Documentary selection",
    title: "Alden holds attention without sounding performative.",
    description: "Best for explainers, premium onboarding, and film-style product narration where the voice should lead quietly.",
    tags: ["Neutral pacing", "Long-form friendly", "Low sibilance"]
  },
  {
    category: "Editorial selection",
    title: "Mina brings crisp structure to lines that need precision.",
    description: "Useful for guided walkthroughs, launch films, and scripts that need authority without unnecessary intensity.",
    tags: ["British cadence", "High clarity", "Brand-safe tone"]
  },
  {
    category: "Cinematic selection",
    title: "Sora lands with softness, space, and a memorable aftertone.",
    description: "Designed for product reveals, culture storytelling, and scenes where the voice should stay close to the image.",
    tags: ["Soft attack", "Global English", "Atmospheric"]
  },
  {
    category: "Localization selection",
    title: "Rafael feels intimate enough for direct address and steady enough for scale.",
    description: "A strong fit for bilingual launches, concierge flows, and regional campaigns that still need premium polish.",
    tags: ["LatAm Spanish", "Warm authority", "Conversation ready"]
  }
];

document.addEventListener("DOMContentLoaded", () => {
  const navToggle = document.querySelector(".nav-toggle");
  const navPanel = document.querySelector(".nav-panel");
  const voiceButtons = document.querySelectorAll(".voice-row");
  const voiceCategory = document.getElementById("voice-category");
  const voiceTitle = document.getElementById("voice-title");
  const voiceDescription = document.getElementById("voice-description");
  const voiceTags = document.getElementById("voice-tags");

  if (navToggle && navPanel) {
    navToggle.addEventListener("click", () => {
      const isOpen = navPanel.classList.toggle("is-open");
      navToggle.setAttribute("aria-expanded", String(isOpen));
    });

    navPanel.querySelectorAll("a").forEach((link) => {
      link.addEventListener("click", () => {
        navPanel.classList.remove("is-open");
        navToggle.setAttribute("aria-expanded", "false");
      });
    });
  }

  const renderVoice = (index) => {
    const voice = voices[index];
    if (!voice) {
      return;
    }

    voiceCategory.textContent = voice.category;
    voiceTitle.textContent = voice.title;
    voiceDescription.textContent = voice.description;
    voiceTags.innerHTML = voice.tags.map((tag) => `<span class="tag">${tag}</span>`).join("");
  };

  voiceButtons.forEach((button) => {
    button.addEventListener("click", () => {
      voiceButtons.forEach((item) => item.classList.remove("is-active"));
      button.classList.add("is-active");
      renderVoice(Number(button.dataset.voice));
    });
  });
});
