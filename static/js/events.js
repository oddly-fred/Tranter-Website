/* events.js — Live countdown clock */
'use strict';

(function () {
  const card = document.getElementById('countdownCard');
  if (!card) return;

  const targetISO = card.dataset.target;
  if (!targetISO) return;

  const targetDate = new Date(targetISO);

  const elDays  = document.getElementById('cd-days');
  const elHours = document.getElementById('cd-hours');
  const elMins  = document.getElementById('cd-mins');
  const elSecs  = document.getElementById('cd-secs');
  const labelEl = card.querySelector('.cd-label');

  // Store previous values so we only flip when changed
  let prev = { days: -1, hours: -1, mins: -1, secs: -1 };

  function pad(n) {
    return String(n).padStart(2, '0');
  }

  function flipIfChanged(el, newVal, prevVal) {
    if (newVal !== prevVal) {
      el.textContent = pad(newVal);
      el.classList.remove('flip');
      // Force reflow to restart animation
      void el.offsetWidth;
      el.classList.add('flip');
    }
    return newVal;
  }

  function tick() {
    const now       = new Date();
    const diffMs    = targetDate - now;

    if (diffMs <= 0) {
      // Event is live or past
      card.classList.add('is-live');
      if (labelEl) labelEl.textContent = '🔴 Event is live now!';
      [elDays, elHours, elMins, elSecs].forEach(el => {
        el.textContent = '00';
        el.classList.add('live-now');
      });
      return; // Stop ticking
    }

    const totalSecs = Math.floor(diffMs / 1000);
    const days      = Math.floor(totalSecs / 86400);
    const hours     = Math.floor((totalSecs % 86400) / 3600);
    const mins      = Math.floor((totalSecs % 3600) / 60);
    const secs      = totalSecs % 60;

    // Update label
    if (labelEl && days === 0 && hours < 1) {
      labelEl.textContent = 'Starting very soon…';
    }

    // Flip only changed units
    prev.days  = flipIfChanged(elDays,  days,  prev.days);
    prev.hours = flipIfChanged(elHours, hours, prev.hours);
    prev.mins  = flipIfChanged(elMins,  mins,  prev.mins);
    prev.secs  = flipIfChanged(elSecs,  secs,  prev.secs);

    // Handle days label — no padding for days
    if (elDays && days !== prev.days - 1) {
      elDays.textContent = days;
    }

    setTimeout(tick, 1000);
  }

  // Start immediately
  tick();
})();
