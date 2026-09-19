/* XMobile Hub — core frontend interactions.
   Every cart / wishlist / color / filter action below runs over fetch()
   so the page never has to reload. */

(function () {
  'use strict';

  function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return '';
  }
  const CSRF_TOKEN = getCookie('csrftoken');

  function toast(message, type = 'success') {
    let stack = document.querySelector('.toast-stack');
    if (!stack) {
      stack = document.createElement('div');
      stack.className = 'toast-stack';
      document.body.appendChild(stack);
    }
    const el = document.createElement('div');
    el.className = `alert alert-${type} shadow-sm mb-0`;
    el.style.minWidth = '260px';
    el.textContent = message;
    stack.appendChild(el);
    setTimeout(() => {
      el.style.transition = 'opacity .4s ease';
      el.style.opacity = '0';
      setTimeout(() => el.remove(), 400);
    }, 2600);
  }
  window.XMH = window.XMH || {};
  window.XMH.toast = toast;

  function postForm(url, data) {
    const formData = new FormData();
    Object.entries(data).forEach(([k, v]) => formData.append(k, v));
    return fetch(url, {
      method: 'POST',
      headers: { 'X-CSRFToken': CSRF_TOKEN },
      body: formData,
    }).then((r) => r.json());
  }
  window.XMH.postForm = postForm;

  /* ---------------------------------------------------------------
     COLOR SWATCH SWAP — product cards on grids + product detail page.
     Clicking a swatch swaps the image client-side, no request needed.
     Re-clicking the same (already active) color is a no-op.
  --------------------------------------------------------------- */
  function initColorSwatches(root = document) {
    root.querySelectorAll('[data-swatch-group]').forEach((group) => {
      const container = group.closest('[data-product-card], [data-pd-root]');
      if (!container) return;
      group.querySelectorAll('.swatch').forEach((swatch) => {
        swatch.addEventListener('click', (e) => {
          e.preventDefault();
          e.stopPropagation();
          if (swatch.classList.contains('active')) return; // same color = no change

          group.querySelectorAll('.swatch').forEach((s) => s.classList.remove('active'));
          swatch.classList.add('active');

          const img = swatch.dataset.image;
          const hoverImg = swatch.dataset.hoverImage || img;
          const variantId = swatch.dataset.variantId;

          const defaultImg = container.querySelector('.thumb-default, [data-pd-main-default]');
          const hoverImgEl = container.querySelector('.thumb-hover img, [data-pd-main-hover]');
          if (defaultImg) defaultImg.src = img;
          if (hoverImgEl) hoverImgEl.src = hoverImg;

          const priceHiddenInput = container.querySelector('[data-variant-input]');
          if (priceHiddenInput) priceHiddenInput.value = variantId || '';

          const colorLabel = container.querySelector('[data-selected-color]');
          if (colorLabel) colorLabel.textContent = swatch.dataset.colorName || '';

          // On the product detail page, also refresh the thumbnail rail highlight
          container.querySelectorAll('.pd-thumb').forEach((t) => t.classList.remove('active'));
          const matchingThumb = container.querySelector(`.pd-thumb[data-variant-id="${variantId}"]`);
          if (matchingThumb) matchingThumb.classList.add('active');
        });
      });
    });

    // Product detail: clicking a thumbnail also swaps the main image
    root.querySelectorAll('.pd-thumb').forEach((thumb) => {
      thumb.addEventListener('click', () => {
        const root2 = thumb.closest('[data-pd-root]');
        if (!root2) return;
        root2.querySelectorAll('.pd-thumb').forEach((t) => t.classList.remove('active'));
        thumb.classList.add('active');
        const mainImg = root2.querySelector('[data-pd-main-default]');
        if (mainImg) mainImg.src = thumb.dataset.image;
        const swatch = root2.querySelector(`.swatch[data-variant-id="${thumb.dataset.variantId}"]`);
        if (swatch) swatch.click();
      });
    });
  }

  /* ---------------------------------------------------------------
     ADD TO CART (grid cards + product detail)
  --------------------------------------------------------------- */
  function initAddToCart(root = document) {
    root.querySelectorAll('.add-cart-btn').forEach((btn) => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        if (btn.disabled) return;
        const container = btn.closest('[data-product-card], [data-pd-root]');
        const productId = btn.dataset.productId;
        const variantInput = container ? container.querySelector('[data-variant-input]') : null;
        const qtyInput = container ? container.querySelector('[data-qty-input]') : null;
        const variantId = variantInput ? variantInput.value : '';
        const quantity = qtyInput ? qtyInput.value : 1;

        btn.disabled = true;
        const originalHtml = btn.innerHTML;
        btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Adding...';

        postForm('/cart/add/', { product_id: productId, variant_id: variantId, quantity })
          .then((data) => {
            if (data.success) {
              updateCartBadge(data.cart_count);
              const miniCartBody = document.querySelector('[data-mini-cart-body]');
              if (miniCartBody) miniCartBody.innerHTML = data.mini_cart_html;
              toast(data.message || 'Added to cart!');
            } else {
              toast(data.message || 'Could not add to cart.', 'danger');
            }
          })
          .catch(() => toast('Something went wrong. Please try again.', 'danger'))
          .finally(() => {
            btn.disabled = false;
            btn.innerHTML = originalHtml;
          });
      });
    });
  }

  function updateCartBadge(count) {
    document.querySelectorAll('[data-cart-count]').forEach((el) => {
      el.textContent = count;
      el.style.display = count > 0 ? 'flex' : 'none';
    });
  }

  /* ---------------------------------------------------------------
     MINI CART PANEL open/close + line item update/remove
  --------------------------------------------------------------- */
  function initMiniCart() {
    const panel = document.querySelector('[data-mini-cart-panel]');
    const overlay = document.querySelector('[data-mini-cart-overlay]');
    if (!panel || !overlay) return;

    document.querySelectorAll('[data-cart-toggle]').forEach((btn) => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        panel.classList.add('open');
        overlay.classList.add('open');
      });
    });
    function close() {
      panel.classList.remove('open');
      overlay.classList.remove('open');
    }
    overlay.addEventListener('click', close);
    const closeBtn = panel.querySelector('[data-mini-cart-close]');
    if (closeBtn) closeBtn.addEventListener('click', close);

    panel.addEventListener('click', (e) => {
      const removeBtn = e.target.closest('[data-cart-remove]');
      if (removeBtn) {
        e.preventDefault();
        postForm('/cart/remove/', { key: removeBtn.dataset.key }).then((data) => {
          updateCartBadge(data.cart_count);
          document.querySelector('[data-mini-cart-body]').innerHTML = data.mini_cart_html;
          toast('Item removed from cart.', 'info');
        });
      }
    });
  }

  /* ---------------------------------------------------------------
     FULL CART PAGE — quantity +/- and remove, live totals via AJAX
  --------------------------------------------------------------- */
  function initCartPage() {
    const table = document.querySelector('[data-cart-table]');
    if (!table) return;

    table.addEventListener('click', (e) => {
      const stepBtn = e.target.closest('[data-qty-step]');
      const removeBtn = e.target.closest('[data-cart-remove-row]');

      if (stepBtn) {
        e.preventDefault();
        const row = stepBtn.closest('[data-cart-row]');
        const input = row.querySelector('input[data-qty]');
        let qty = parseInt(input.value, 10) || 1;
        qty += stepBtn.dataset.qtyStep === 'inc' ? 1 : -1;
        if (qty < 1) qty = 1;
        input.value = qty;
        updateCartRow(row.dataset.key, qty);
      }
      if (removeBtn) {
        e.preventDefault();
        const row = removeBtn.closest('[data-cart-row]');
        updateCartRow(row.dataset.key, 0);
      }
    });

    table.addEventListener('change', (e) => {
      if (e.target.matches('input[data-qty]')) {
        const row = e.target.closest('[data-cart-row]');
        let qty = parseInt(e.target.value, 10) || 1;
        updateCartRow(row.dataset.key, qty);
      }
    });

    function updateCartRow(key, quantity) {
      const url = quantity > 0 ? '/cart/update/' : '/cart/remove/';
      const payload = quantity > 0 ? { key, quantity } : { key };
      postForm(url, payload).then((data) => {
        document.querySelector('[data-cart-page-body]').innerHTML = data.cart_table_html;
        updateCartBadge(data.cart_count);
        const totalEl = document.querySelector('[data-cart-total]');
        if (totalEl) totalEl.textContent = data.cart_total_display;
        toast(quantity > 0 ? 'Cart updated.' : 'Item removed.', 'info');
      });
    }
  }

  /* ---------------------------------------------------------------
     WISHLIST TOGGLE
  --------------------------------------------------------------- */
  function initWishlist(root = document) {
    root.querySelectorAll('.wishlist-btn').forEach((btn) => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        const productId = btn.dataset.productId;
        postForm(`/shop/wishlist/${productId}/toggle/`, {}).then((data) => {
          if (data.success) {
            btn.classList.toggle('active', data.in_wishlist);
            toast(data.in_wishlist ? 'Added to wishlist ❤' : 'Removed from wishlist', 'info');
          } else if (data.message) {
            toast(data.message, 'warning');
          }
        }).catch(() => { window.location.href = '/account/login/'; });
      });
    });
  }

  /* ---------------------------------------------------------------
     SHOP FILTER / SORT — replaces the product grid without reload
  --------------------------------------------------------------- */
  function initShopFilters() {
    const shopRoot = document.querySelector('[data-shop-root]');
    if (!shopRoot) return;
    const grid = document.querySelector('[data-product-grid]');
    const pagination = document.querySelector('[data-pagination]');
    const countEl = document.querySelector('[data-result-count]');

    const filterUrl = shopRoot.dataset.filterUrl;

    function fetchAndRender(params, pushHistory = true) {
      grid.style.opacity = '0.4';
      fetch(`${filterUrl}?${params.toString()}`)
        .then((r) => r.json())
        .then((data) => {
          grid.innerHTML = data.html;
          if (pagination) pagination.innerHTML = data.pagination_html;
          if (countEl) countEl.textContent = data.count;
          grid.style.opacity = '1';
          initColorSwatches(grid);
          initAddToCart(grid);
          initWishlist(grid);
          if (pushHistory) {
            const newUrl = `${window.location.pathname}?${params.toString()}`;
            window.history.pushState({}, '', newUrl);
          }
        });
    }

    function currentParams() {
      return new URLSearchParams(window.location.search);
    }

    shopRoot.querySelectorAll('[data-filter-input]').forEach((input) => {
      input.addEventListener('change', () => {
        const params = currentParams();
        if (input.value) params.set(input.dataset.filterInput, input.value);
        else params.delete(input.dataset.filterInput);
        params.delete('page');
        fetchAndRender(params);
      });
    });

    const searchInput = shopRoot.querySelector('[data-shop-search]');
    if (searchInput) {
      let debounce;
      searchInput.addEventListener('input', () => {
        clearTimeout(debounce);
        debounce = setTimeout(() => {
          const params = currentParams();
          if (searchInput.value) params.set('q', searchInput.value);
          else params.delete('q');
          params.delete('page');
          fetchAndRender(params);
        }, 350);
      });
    }

    document.addEventListener('click', (e) => {
      const pageLink = e.target.closest('[data-page-link]');
      if (pageLink) {
        e.preventDefault();
        const params = currentParams();
        params.set('page', pageLink.dataset.pageLink);
        fetchAndRender(params);
        window.scrollTo({ top: shopRoot.offsetTop - 90, behavior: 'smooth' });
      }
    });
  }

  /* ---------------------------------------------------------------
     NAVBAR SEARCH SUGGESTIONS
  --------------------------------------------------------------- */
  function initSearchSuggest() {
    const input = document.querySelector('[data-nav-search-input]');
    const box = document.querySelector('[data-nav-search-suggest]');
    if (!input || !box) return;
    let debounce;
    input.addEventListener('input', () => {
      clearTimeout(debounce);
      const q = input.value.trim();
      if (q.length < 2) { box.classList.remove('show'); return; }
      debounce = setTimeout(() => {
        fetch(`/shop/search-suggest/?q=${encodeURIComponent(q)}`)
          .then((r) => r.json())
          .then((data) => {
            if (!data.results.length) { box.classList.remove('show'); return; }
            box.innerHTML = data.results.map((p) => `
              <a href="${p.url}" class="search-suggest-item text-decoration-none text-dark">
                <img src="${p.image}" alt="">
                <div>
                  <div class="fw-semibold small">${p.brand} ${p.name}</div>
                  <div class="text-accent small">Rs. ${Number(p.price).toLocaleString()}</div>
                </div>
              </a>`).join('');
            box.classList.add('show');
          });
      }, 300);
    });
    document.addEventListener('click', (e) => {
      if (!box.contains(e.target) && e.target !== input) box.classList.remove('show');
    });
  }

  /* ---------------------------------------------------------------
     NEWSLETTER SUBSCRIBE
  --------------------------------------------------------------- */
  function initNewsletter() {
    const form = document.querySelector('[data-newsletter-form]');
    if (!form) return;
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const email = form.querySelector('input[type=email]').value;
      postForm('/newsletter/subscribe/', { email }).then((data) => {
        toast(data.message, data.success ? 'success' : 'warning');
        if (data.success) form.reset();
      });
    });
  }

  /* ---------------------------------------------------------------
     QUANTITY STEPPER (product detail page)
  --------------------------------------------------------------- */
  function initQtyStepper(root = document) {
    root.querySelectorAll('.qty-stepper').forEach((stepper) => {
      const input = stepper.querySelector('input');
      stepper.querySelectorAll('button').forEach((btn) => {
        btn.addEventListener('click', () => {
          let val = parseInt(input.value, 10) || 1;
          val += btn.dataset.step === 'inc' ? 1 : -1;
          const max = parseInt(input.max, 10) || 99;
          if (val < 1) val = 1;
          if (val > max) val = max;
          input.value = val;
        });
      });
    });
  }

  document.addEventListener('DOMContentLoaded', () => {
    initColorSwatches();
    initAddToCart();
    initMiniCart();
    initCartPage();
    initWishlist();
    initShopFilters();
    initSearchSuggest();
    initNewsletter();
    initQtyStepper();

    // Bootstrap toast-style dismissible alerts already on page (Django messages)
    document.querySelectorAll('[data-auto-dismiss]').forEach((el) => {
      setTimeout(() => { el.style.display = 'none'; }, 4000);
    });
  });
})();
