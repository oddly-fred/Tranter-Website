'use strict';

/* ═══════════════════════════════════════════════════
   base.js — Nav, Mega Menu, Drawer,
   Tranter IT
═══════════════════════════════════════════════════ */

/* ── NAV SCROLL SHADOW ───────────────────────────── */
(function () {
  const nav = document.getElementById('nav');
  if (!nav) return;
  window.addEventListener('scroll', () => {
    nav.classList.toggle('scrolled', window.scrollY > 40);
  }, { passive: true });
})();


/* ── MOBILE DRAWER ───────────────────────────────── */
const burger   = document.getElementById('burger');
const drawer   = document.getElementById('drawer');
const overlay  = document.getElementById('overlay');
const dClose   = document.getElementById('drawerClose');

function openMobileDrawer() {
  drawer?.classList.add('open');
  overlay?.classList.add('open');
  burger?.classList.add('open');
  burger?.setAttribute('aria-expanded', 'true');
  document.body.style.overflow = 'hidden';
}

function closeMobileDrawer() {
  drawer?.classList.remove('open');
  overlay?.classList.remove('open');
  burger?.classList.remove('open');
  burger?.setAttribute('aria-expanded', 'false');
  document.body.style.overflow = '';
}

burger?.addEventListener('click', () => {
  drawer?.classList.contains('open') ? closeMobileDrawer() : openMobileDrawer();
});
dClose?.addEventListener('click', closeMobileDrawer);
overlay?.addEventListener('click', closeMobileDrawer);


/* ── DRAWER ACCORDION ────────────────────────────── */
function toggleDrawerAcc(btn) {
  const panel = btn.nextElementSibling;
  const isOpen = panel?.classList.contains('open');
  // Close all
  document.querySelectorAll('.drawer-acc-panel.open').forEach(p => p.classList.remove('open'));
  document.querySelectorAll('.drawer-acc-trigger.open').forEach(b => b.classList.remove('open'));
  // Open clicked (unless was already open)
  if (!isOpen && panel) {
    panel.classList.add('open');
    btn.classList.add('open');
  }
}


function submitDemo() {
    document.getElementById("step3").classList.remove("active");
    document.getElementById("success").classList.add("active");

    if (REGION_CONTENT.is_nigeria) {
        setTimeout(() => {
            window.open(REGION_CONTENT.whatsapp_link);
        }, 1500);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const phoneInput = document.getElementById("d_phone");
    if(phoneInput) phoneInput.placeholder = REGION_CONTENT.is_nigeria ? "+234 800 000 0000" : "+1 000 000 0000";
});



document.addEventListener("DOMContentLoaded", function () {
  const mega = document.querySelector(".has-mega");
  const trigger = mega?.querySelector(".mega-trigger");

  if (!mega || !trigger) return;

  trigger.addEventListener("click", function (e) {
    e.preventDefault();
    mega.classList.toggle("mega-open");
  });

  // Close when clicking outside
  document.addEventListener("click", function (e) {
    if (!mega.contains(e.target)) {
      mega.classList.remove("mega-open");
    }
  });
});