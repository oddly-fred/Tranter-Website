/* home.js — homepage only */
'use strict';
// ── Hero Slider ───────────────────────────────────
(function () {
const slides  = document.querySelectorAll('.hero-slides .slide');
const copies  = document.querySelectorAll('.slide-copy');
const dots    = document.querySelectorAll('.sdot');
if (!slides.length) return;
let cur = 0;
let timer = null;
function goTo(n) {
slides[cur].classList.remove('active');
copies[cur]?.classList.remove('active');
dots[cur]?.classList.remove('active');
cur = (n + slides.length) % slides.length;
slides[cur].classList.add('active');
copies[cur]?.classList.add('active');
dots[cur]?.classList.add('active');
}
function start() {
clearInterval(timer);
timer = setInterval(() => goTo(cur + 1), 5800);
}
// Dot clicks
dots.forEach(dot => {
dot.addEventListener('click', () => { goTo(+dot.dataset.i); start(); });
});
// Touch swipe on hero
let touchX = 0;
const heroEl = document.getElementById('hero');
heroEl?.addEventListener('touchstart', e => { touchX = e.touches[0].clientX; }, { passive: true });
heroEl?.addEventListener('touchend',   e => {
const dx = e.changedTouches[0].clientX - touchX;
if (Math.abs(dx) > 48) { goTo(dx < 0 ? cur + 1 : cur - 1); start(); }
}, { passive: true });
start();
})();
// ── Stat counter animation ────────────────────────
(function () {
const els = document.querySelectorAll('.counter');
if (!els.length) return;
const io = new IntersectionObserver((entries) => {
entries.forEach(entry => {
if (!entry.isIntersecting) return;
const el     = entry.target;
const target = parseInt(el.dataset.target, 10);
let startTs  = null;
const DURATION = 1800;
function tick(ts) {
if (!startTs) startTs = ts;
const elapsed  = Math.min(ts - startTs, DURATION);
const progress = elapsed / DURATION;
// Cubic ease-out
const eased    = 1 - Math.pow(1 - progress, 3);
el.textContent = Math.floor(eased * target);
if (elapsed < DURATION) {
requestAnimationFrame(tick);
} else {
el.textContent = target;
}
}
requestAnimationFrame(tick);
io.unobserve(el);
});
}, { threshold: 0.5 });
els.forEach(el => io.observe(el));
})();