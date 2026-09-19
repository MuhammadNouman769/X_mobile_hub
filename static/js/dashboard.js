/* XMobile Hub — dashboard interactions: live KPI polling, AJAX delete,
   and inline order-status updates. No admin panel, no page reloads. */
(function () {
  'use strict';

  function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return '';
  }
  const CSRF_TOKEN = getCookie('csrftoken');

  function postForm(url, data) {
    const formData = new FormData();
    Object.entries(data).forEach(([k, v]) => formData.append(k, v));
    return fetch(url, { method: 'POST', headers: { 'X-CSRFToken': CSRF_TOKEN }, body: formData }).then((r) => r.json());
  }

  /* -------- Live stats polling (dashboard home only) -------- */
  function pollLiveStats() {
    const liveUrl = document.body.dataset.liveStatsUrl;
    if (!liveUrl) return;
    fetch(liveUrl).then((r) => r.json()).then((data) => {
      const map = {
        'live-total-stock': data.total_stock_units,
        'live-low-stock': data.low_stock_count,
        'live-out-stock': data.out_of_stock_count,
        'live-today-orders': data.today_orders_count,
        'live-total-orders': data.total_orders,
      };
      Object.entries(map).forEach(([id, val]) => {
        const el = document.getElementById(id);
        if (el) el.textContent = val;
      });
      const revenueEl = document.getElementById('live-today-revenue');
      if (revenueEl) revenueEl.textContent = 'Rs. ' + Number(data.today_revenue).toLocaleString();
      const clock = document.getElementById('server-clock');
      if (clock) clock.textContent = data.server_time;
    }).catch(() => {});
  }

  /* -------- Generic AJAX delete with confirm -------- */
  function initAjaxDelete() {
    document.addEventListener('click', (e) => {
      const btn = e.target.closest('[data-ajax-delete]');
      if (!btn) return;
      e.preventDefault();
      const label = btn.dataset.label || 'this item';
      if (!confirm(`Delete ${label}? This cannot be undone.`)) return;
      postForm(btn.dataset.ajaxDelete, {}).then((data) => {
        if (data.success) {
          const row = btn.closest('tr, [data-row]');
          if (row) row.remove();
          window.XMH && window.XMH.toast ? window.XMH.toast(data.message || 'Deleted successfully.') : null;
        }
      });
    });
  }

  /* -------- Inline order status update -------- */
  function initOrderStatusUpdate() {
    document.querySelectorAll('[data-order-status-select]').forEach((select) => {
      select.addEventListener('change', () => {
        const url = select.dataset.orderStatusSelect;
        postForm(url, { status: select.value }).then((data) => {
          if (data.success) {
            const badge = document.querySelector(`[data-order-status-badge="${select.dataset.orderId}"]`);
            if (badge) {
              badge.textContent = data.status_display;
              badge.className = `badge bg-${data.badge_class}`;
            }
          }
        });
      });
    });
  }

  document.addEventListener('DOMContentLoaded', () => {
    pollLiveStats();
    setInterval(pollLiveStats, 8000);
    initAjaxDelete();
    initOrderStatusUpdate();
  });
})();
