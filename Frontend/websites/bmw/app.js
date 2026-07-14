// BMW Corporate Interactive Script

document.addEventListener('DOMContentLoaded', () => {
  
  // ==========================================
  // SPA Tab Navigation
  // ==========================================
  const navLinks = document.querySelectorAll('.top-nav__link, .mobile-nav-overlay__link');
  const sections = document.querySelectorAll('.view-section');
  const mobileNav = document.getElementById('mobile-nav');
  const hamburgerBtn = document.getElementById('hamburger-btn');

  function switchTab(targetId) {
    // Hide all sections
    sections.forEach(sec => sec.classList.remove('active'));
    // Show target section
    const targetSection = document.getElementById(targetId);
    if (targetSection) {
      targetSection.classList.add('active');
    }

    // Update active class on nav links
    navLinks.forEach(link => {
      if (link.getAttribute('data-target') === targetId) {
        link.classList.add('active');
      } else {
        link.classList.remove('active');
      }
    });

    // Close mobile nav if open
    mobileNav.classList.remove('open');
    hamburgerBtn.classList.remove('open');

    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  navLinks.forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      const targetId = link.getAttribute('data-target');
      switchTab(targetId);
    });
  });

  // Logo acts as Home button
  document.getElementById('logo-nav').addEventListener('click', (e) => {
    e.preventDefault();
    switchTab('home-view');
  });

  // Hero CTAs
  document.getElementById('hero-btn-config').addEventListener('click', () => {
    switchTab('configurator-view');
  });

  document.getElementById('hero-btn-explore').addEventListener('click', () => {
    // Scroll to showcase section
    const showcaseSec = document.querySelector('.hero-photo-band');
    if (showcaseSec) {
      showcaseSec.scrollIntoView({ behavior: 'smooth' });
    }
  });

  document.getElementById('btn-home-inventory').addEventListener('click', () => {
    switchTab('inventory-view');
  });

  // Model card CTAs & Footer links
  document.querySelectorAll('[data-action="go-config"]').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const model = btn.getAttribute('data-model');
      switchTab('configurator-view');
      if (model) {
        selectConfigModel(model);
      }
    });
  });

  // Hamburger button
  hamburgerBtn.addEventListener('click', () => {
    const isOpen = mobileNav.classList.toggle('open');
    hamburgerBtn.classList.toggle('open', isOpen);
  });

  // ==========================================
  // Configurator Logic
  // ==========================================
  const configPreviewImg = document.getElementById('config-preview-img');
  const configCarTitle = document.getElementById('config-car-title');
  const configCarCategory = document.getElementById('config-car-category');
  const specRange = document.getElementById('spec-range');
  const specAcceleration = document.getElementById('spec-acceleration');
  const specPower = document.getElementById('spec-power');
  
  const paintOptionsContainer = document.getElementById('paint-options');
  const wheelOptionsContainer = document.getElementById('wheel-options');
  const upholsteryOptionsContainer = document.getElementById('upholstery-options');

  const baseMsrpValue = document.getElementById('base-msrp-value');
  const optionsTotalValue = document.getElementById('options-total-value');
  const totalPriceValue = document.getElementById('total-price-value');

  // Model Specs Database
  const modelSpecs = {
    i7: {
      name: "BMW i7 xDrive60",
      category: "Sedan · Fully Electric",
      range: "Up to 387 mi",
      acceleration: "3.5s",
      power: "536 hp",
      baseMsrp: 124200,
      paints: [
        { name: "Carbon Black Metallic", hex: "#11151c", image: "assets/i7_black.png", price: 0, id: "carbon-black" },
        { name: "Mineral White Metallic", hex: "#f7f7f7", image: "assets/i7_white.png", price: 650, id: "mineral-white" }
      ]
    },
    ix: {
      name: "BMW iX xDrive50",
      category: "SUV · Fully Electric",
      range: "Up to 307 mi",
      acceleration: "4.4s",
      power: "516 hp",
      baseMsrp: 87250,
      paints: [
        { name: "Mineral White Metallic", hex: "#f7f7f7", image: "assets/ix_white.png", price: 0, id: "mineral-white" },
        { name: "Phytonic Blue Metallic", hex: "#1c518a", image: "assets/ix_white.png", price: 650, id: "phytonic-blue", filter: "hue-rotate(200deg) saturate(1.2)" }
      ]
    }
  };

  let currentModel = 'i7';
  let selectedPaintPrice = 0;
  let selectedWheelsPrice = 0;
  let selectedUpholsteryPrice = 0;

  function selectConfigModel(modelId) {
    if (!modelSpecs[modelId]) return;
    currentModel = modelId;

    // Update active tab in config selector
    document.querySelectorAll('.configurator-panel__model-selector .category-tab').forEach(tab => {
      if (tab.getAttribute('data-model') === modelId) {
        tab.classList.add('category-tab-active');
      } else {
        tab.classList.remove('category-tab-active');
      }
    });

    const spec = modelSpecs[modelId];
    
    // Update labels
    configCarTitle.innerText = spec.name;
    configCarCategory.innerText = spec.category;
    specRange.innerText = spec.range;
    specAcceleration.innerText = spec.acceleration;
    specPower.innerText = spec.power;

    // Reset option selections & prices
    selectedPaintPrice = 0;
    selectedWheelsPrice = 0;
    selectedUpholsteryPrice = 0;

    // Redraw Paint Options
    paintOptionsContainer.innerHTML = '';
    spec.paints.forEach((paint, idx) => {
      const btn = document.createElement('button');
      btn.className = `configurator-option-tile ${idx === 0 ? 'configurator-option-tile-selected' : ''}`;
      btn.dataset.paint = paint.id;
      btn.dataset.image = paint.image;
      btn.dataset.price = paint.price;
      if (paint.filter) btn.dataset.filter = paint.filter;

      btn.innerHTML = `
        <div class="configurator-option-tile__color-dot" style="background-color: ${paint.hex};"></div>
        <span class="title-sm" style="font-size: 14px;">${paint.name}</span>
        <span class="caption">${paint.price === 0 ? 'Included' : '+$' + paint.price}</span>
      `;
      paintOptionsContainer.appendChild(btn);
    });

    // Reset Wheels & Upholstery styling to first elements
    document.querySelectorAll('#wheel-options .configurator-option-tile').forEach((tile, idx) => {
      if (idx === 0) {
        tile.classList.add('configurator-option-tile-selected');
      } else {
        tile.classList.remove('configurator-option-tile-selected');
      }
    });
    document.querySelectorAll('#upholstery-options .configurator-option-tile').forEach((tile, idx) => {
      if (idx === 0) {
        tile.classList.add('configurator-option-tile-selected');
      } else {
        tile.classList.remove('configurator-option-tile-selected');
      }
    });

    // Update Image Preview
    updatePreviewImage();
    
    // Recalculate Pricing
    calculatePrices();

    // Rebind paint clicks
    bindPaintClickHandlers();
  }

  function updatePreviewImage() {
    const activePaintTile = paintOptionsContainer.querySelector('.configurator-option-tile-selected');
    if (activePaintTile) {
      configPreviewImg.style.opacity = '0';
      setTimeout(() => {
        configPreviewImg.src = activePaintTile.dataset.image;
        if (activePaintTile.dataset.filter) {
          configPreviewImg.style.filter = activePaintTile.dataset.filter;
        } else {
          configPreviewImg.style.filter = 'none';
        }
        configPreviewImg.style.opacity = '1';
      }, 150);
    }
  }

  function calculatePrices() {
    const spec = modelSpecs[currentModel];
    const basePrice = spec.baseMsrp;
    const optionsTotal = selectedPaintPrice + selectedWheelsPrice + selectedUpholsteryPrice;
    const totalPrice = basePrice + optionsTotal;

    baseMsrpValue.innerText = `$${basePrice.toLocaleString()}`;
    optionsTotalValue.innerText = `$${optionsTotal.toLocaleString()}`;
    totalPriceValue.innerText = `$${totalPrice.toLocaleString()}`;
  }

  // Model selection tabs inside configurator panel
  document.querySelectorAll('.configurator-panel__model-selector .category-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      const model = tab.getAttribute('data-model');
      selectConfigModel(model);
    });
  });

  // Click handlers for Paints
  function bindPaintClickHandlers() {
    paintOptionsContainer.querySelectorAll('.configurator-option-tile').forEach(tile => {
      tile.addEventListener('click', () => {
        paintOptionsContainer.querySelectorAll('.configurator-option-tile').forEach(t => t.classList.remove('configurator-option-tile-selected'));
        tile.classList.add('configurator-option-tile-selected');
        selectedPaintPrice = parseInt(tile.dataset.price) || 0;
        updatePreviewImage();
        calculatePrices();
      });
    });
  }

  // Click handlers for Wheels
  document.querySelectorAll('#wheel-options .configurator-option-tile').forEach(tile => {
    tile.addEventListener('click', () => {
      document.querySelectorAll('#wheel-options .configurator-option-tile').forEach(t => t.classList.remove('configurator-option-tile-selected'));
      tile.classList.add('configurator-option-tile-selected');
      selectedWheelsPrice = parseInt(tile.dataset.price) || 0;
      calculatePrices();
    });
  });

  // Click handlers for Upholstery
  document.querySelectorAll('#upholstery-options .configurator-option-tile').forEach(tile => {
    tile.addEventListener('click', () => {
      document.querySelectorAll('#upholstery-options .configurator-option-tile').forEach(t => t.classList.remove('configurator-option-tile-selected'));
      tile.classList.add('configurator-option-tile-selected');
      selectedUpholsteryPrice = parseInt(tile.dataset.price) || 0;
      calculatePrices();
    });
  });

  // Initialize configurator handlers
  bindPaintClickHandlers();

  // Reservation action
  document.getElementById('btn-order-config').addEventListener('click', () => {
    const spec = modelSpecs[currentModel];
    const total = totalPriceValue.innerText;
    alert(`Success! Your configuration for ${spec.name} has been reserved. Total Price: ${total}. Our representatives will contact you shortly.`);
  });


  // ==========================================
  // Inventory Filtering Logic
  // ==========================================
  const searchInput = document.getElementById('search-input');
  const inventoryGrid = document.getElementById('inventory-card-grid');
  const inventoryCards = document.querySelectorAll('.inventory-card');
  const inventoryCountLabel = document.getElementById('inventory-count');
  
  const bodyChips = document.querySelectorAll('#filter-body-style .filter-chip');
  const fuelChips = document.querySelectorAll('#filter-fuel-type .filter-chip');
  const priceChips = document.querySelectorAll('#filter-price-range .filter-chip');

  let activeFilters = {
    search: '',
    body: 'all',
    fuel: 'all',
    price: 'all'
  };

  function filterInventory() {
    let visibleCount = 0;

    inventoryCards.forEach(card => {
      const name = card.getAttribute('data-name').toLowerCase();
      const body = card.getAttribute('data-body');
      const fuel = card.getAttribute('data-fuel');
      const price = parseInt(card.getAttribute('data-price')) || 0;

      // Check search match
      const searchMatch = name.includes(activeFilters.search.toLowerCase());
      
      // Check body style match
      const bodyMatch = activeFilters.body === 'all' || body === activeFilters.body;

      // Check fuel match
      const fuelMatch = activeFilters.fuel === 'all' || fuel === activeFilters.fuel;

      // Check price match
      let priceMatch = true;
      if (activeFilters.price === 'under-100k') {
        priceMatch = price < 100000;
      } else if (activeFilters.price === 'over-100k') {
        priceMatch = price >= 100000;
      }

      if (searchMatch && bodyMatch && fuelMatch && priceMatch) {
        card.style.display = 'flex';
        visibleCount++;
      } else {
        card.style.display = 'none';
      }
    });

    inventoryCountLabel.innerText = `Showing ${visibleCount} vehicle${visibleCount === 1 ? '' : 's'}`;
  }

  // Bind search input
  searchInput.addEventListener('input', (e) => {
    activeFilters.search = e.target.value;
    filterInventory();
  });

  // Helper to toggle active chip
  function setupChipGroup(chips, filterKey) {
    chips.forEach(chip => {
      chip.addEventListener('click', () => {
        chips.forEach(c => c.classList.remove('filter-chip-active'));
        chip.classList.add('filter-chip-active');
        activeFilters[filterKey] = chip.getAttribute('data-filter');
        filterInventory();
      });
    });
  }

  setupChipGroup(bodyChips, 'body');
  setupChipGroup(fuelChips, 'fuel');
  setupChipGroup(priceChips, 'price');

  // Reset Filters button
  document.getElementById('btn-reset-filters').addEventListener('click', () => {
    activeFilters = {
      search: '',
      body: 'all',
      fuel: 'all',
      price: 'all'
    };

    searchInput.value = '';
    
    // Reset chip active classes
    [bodyChips, fuelChips, priceChips].forEach(group => {
      group.forEach((chip, idx) => {
        if (idx === 0) {
          chip.classList.add('filter-chip-active');
        } else {
          chip.classList.remove('filter-chip-active');
        }
      });
    });

    filterInventory();
  });

  // Reserve actions inside catalog
  inventoryGrid.addEventListener('click', (e) => {
    const reserveBtn = e.target.closest('[data-action="reserve"]');
    if (reserveBtn) {
      const card = reserveBtn.closest('.inventory-card');
      const name = card.getAttribute('data-name');
      const price = parseInt(card.getAttribute('data-price')).toLocaleString();
      alert(`Success! You have reserved ${name} for $${price}. A dealer representative will reach out to verify.`);
    }
  });

  // Pre-footer Book Test Drive trigger
  document.getElementById('btn-cta-testdrive').addEventListener('click', () => {
    alert("Test drive booking form: Please select your dealer and time. (Feature coming soon!)");
  });

  // ==========================================
  // Cookie Consent Banner Logic
  // ==========================================
  const cookieBanner = document.getElementById('cookie-banner');
  const cookieAcceptBtn = document.getElementById('cookie-accept-btn');
  const cookieDeclineBtn = document.getElementById('cookie-decline-btn');

  // Check if user already made choice
  const cookieChoice = localStorage.getItem('bmw-cookie-choice');
  if (!cookieChoice) {
    // Show banner after 1.5 seconds delay
    setTimeout(() => {
      cookieBanner.classList.add('show');
    }, 1500);
  }

  cookieAcceptBtn.addEventListener('click', () => {
    localStorage.setItem('bmw-cookie-choice', 'accepted');
    cookieBanner.classList.remove('show');
  });

  cookieDeclineBtn.addEventListener('click', () => {
    localStorage.setItem('bmw-cookie-choice', 'declined');
    cookieBanner.classList.remove('show');
  });

});
