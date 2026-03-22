'use strict';

/* ═══════════════════════════════════════════════════
   home.js — Hero slider + text fade-in + stat counters
   Tranter IT
═══════════════════════════════════════════════════ */

(function () {

  /* ──────────────────────────────────────────────────
     1. HERO SLIDER
     Slides background images/video. Syncs headline
     copy with a staggered word-by-word fade-in.
  ────────────────────────────────────────────────── */
  const slidesEl  = document.getElementById('heroSlides');
  const dotsEl    = document.getElementById('slideDots');
  const copiesEl  = document.querySelectorAll('.slide-copy');
  const slideEls  = slidesEl ? slidesEl.querySelectorAll('.slide') : [];
  const dotEls    = dotsEl   ? dotsEl.querySelectorAll('.sdot')    : [];

  let current   = 0;
  let timer     = null;
  const DURATION = 5800;   // ms between auto-advances

  function goTo(index) {
    const total = slideEls.length;
    if (!total) return;

    // Clamp index
    index = ((index % total) + total) % total;

    // ── Background slides
    slideEls[current].classList.remove('active');
    slideEls[index].classList.add('active');

    // ── Dot indicators
    dotEls.forEach((d, i) => d.classList.toggle('active', i === index));

    // ── Text copies: fade out old, fade in new
    if (copiesEl[current]) {
      copiesEl[current].classList.remove('active');
      copiesEl[current].classList.add('leaving');
      const leaving = copiesEl[current];
      setTimeout(() => leaving.classList.remove('leaving'), 700);
    }
    if (copiesEl[index]) {
      copiesEl[index].classList.add('active');
      // Stagger the headline words
      staggerWords(copiesEl[index]);
    }

    current = index;
  }

  function staggerWords(copyEl) {
    // Split headline spans into individual word spans for stagger
    const headline = copyEl.querySelector('.h-headline');
    const sub      = copyEl.querySelector('.h-sub');
    const actions  = copyEl.closest('.hero-left')
                       ? copyEl.closest('.hero-left').querySelector('.h-actions')
                       : null;

    // Animate headline lines
    if (headline) {
      headline.style.animation = 'none';
      void headline.offsetWidth; // reflow
      headline.style.animation = '';
    }

    // Cascade sub and actions
    [sub, actions].forEach((el, i) => {
      if (!el) return;
      el.style.opacity    = '0';
      el.style.transform  = 'translateY(18px)';
      el.style.transition = 'none';
      void el.offsetWidth;
      el.style.transition = `opacity .65s ease ${0.35 + i * 0.15}s,
                              transform .65s ease ${0.35 + i * 0.15}s`;
      el.style.opacity    = '1';
      el.style.transform  = 'translateY(0)';
    });
  }

  function startTimer() {
    clearInterval(timer);
    timer = setInterval(() => goTo(current + 1), DURATION);
  }

  // Dot click
  dotEls.forEach(dot => {
    dot.addEventListener('click', () => {
      goTo(parseInt(dot.dataset.i, 10));
      startTimer();
    });
  });

  // Touch swipe support
  let touchStartX = 0;
  if (slidesEl) {
    slidesEl.addEventListener('touchstart', e => {
      touchStartX = e.touches[0].clientX;
    }, { passive: true });

    slidesEl.addEventListener('touchend', e => {
      const dx = e.changedTouches[0].clientX - touchStartX;
      if (Math.abs(dx) > 50) {
        goTo(dx < 0 ? current + 1 : current - 1);
        startTimer();
      }
    }, { passive: true });
  }

  // Kick off
  if (slideEls.length > 1) {
    staggerWords(copiesEl[0]);
    startTimer();
  }


  /* ──────────────────────────────────────────────────
     2. SCROLL FADE-IN
     Animates elements with .fade-up class when they
     enter the viewport (also runs on section headers,
     cards, etc. via IntersectionObserver).
  ────────────────────────────────────────────────── */
  const fadeTargets = document.querySelectorAll(
    '.svc-card, .pillar, .sector-card, .process-step, ' +
    '.ev-card, .ins-card, .client-cell, ' +
    '.section-hdr, .who-left, .who-right, ' +
    '.why-left, .why-right, .iso-card, .perf-card, ' +
    '.stat-item, .value-card'
  );

  if ('IntersectionObserver' in window) {
    const fadeObs = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('in-view');
          fadeObs.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });

    fadeTargets.forEach((el, i) => {
      // Stagger delay based on position in its parent
      const siblings = el.parentElement
        ? Array.from(el.parentElement.children)
        : [];
      const sibIndex = siblings.indexOf(el);
      el.style.setProperty('--fade-delay', `${sibIndex * 0.07}s`);
      fadeObs.observe(el);
    });
  } else {
    // Fallback: show everything immediately
    fadeTargets.forEach(el => el.classList.add('in-view'));
  }


  /* ──────────────────────────────────────────────────
     3. STAT COUNTERS
     Counts up from 0 to target value when the stats
     band scrolls into view.
  ────────────────────────────────────────────────── */
  const counters = document.querySelectorAll('.counter');

  function easeOutCubic(t) {
    return 1 - Math.pow(1 - t, 3);
  }

  function animateCounter(el) {
    const target   = parseInt(el.dataset.target, 10);
    const duration = 1800;
    const start    = performance.now();

    function step(now) {
      const elapsed  = now - start;
      const progress = Math.min(elapsed / duration, 1);
      const eased    = easeOutCubic(progress);
      el.textContent = Math.floor(eased * target);
      if (progress < 1) requestAnimationFrame(step);
      else el.textContent = target;
    }
    requestAnimationFrame(step);
  }

  if ('IntersectionObserver' in window && counters.length) {
    const counterObs = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.querySelectorAll('.counter').forEach(animateCounter);
          counterObs.unobserve(entry.target);
        }
      });
    }, { threshold: 0.4 });

    const statsBand = document.querySelector('.stats-band');
    if (statsBand) counterObs.observe(statsBand);
  }


  /* ──────────────────────────────────────────────────
     4. TRUST STRIP — duplicate items for seamless loop
     If items were rendered server-side, clone them so
     the CSS marquee animation loops without a gap.
  ────────────────────────────────────────────────── */
  const track = document.getElementById('trustTrack');
  if (track) {
    const items = track.innerHTML;
    // Only duplicate if not already duplicated ({% empty %} block does it)
    const count = track.children.length;
    if (count > 0 && count <= 18) {
      track.innerHTML = items + items;
    }
  }

})();