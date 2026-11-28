/**
 * Landing page motion: particle heart, scroll story, reveals and flip cards.
 * No external libraries. The page stays readable if this file does not load.
 */
(function () {
    'use strict';

    const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
    document.documentElement.classList.add('lp-js');

    // ─── Particle heart ───────────────────────────────────────────
    function particleHeart(canvas) {
        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        const BPM = 72;
        const pointer = { x: -9999, y: -9999 };
        let particles = [];
        let size = 0;
        let frame = 0;
        let onScreen = true;

        // Classic heart curve, roughly -16…16 wide
        function heartPoint(t, scale) {
            return {
                x: 16 * Math.pow(Math.sin(t), 3) * scale,
                y: -(13 * Math.cos(t) - 5 * Math.cos(2 * t) - 2 * Math.cos(3 * t) - Math.cos(4 * t)) * scale
            };
        }

        function build() {
            size = canvas.clientWidth;
            if (!size) return;
            const ratio = Math.min(window.devicePixelRatio || 1, 2);
            canvas.width = canvas.height = size * ratio;
            ctx.setTransform(ratio, 0, 0, ratio, 0, 0);

            const count = size < 380 ? 850 : 1700;
            const unit = size / 40;
            particles = Array.from({ length: count }, (_, i) => {
                // A third draws the outline, the rest fills the inside
                const fill = i % 3 === 0 ? 1 : Math.sqrt(Math.random());
                const home = heartPoint(Math.random() * Math.PI * 2, unit * fill);
                return {
                    hx: home.x, hy: home.y,
                    x: (Math.random() - 0.5) * size, y: (Math.random() - 0.5) * size,
                    vx: 0, vy: 0,
                    r: 0.9 + Math.random() * 1.9,
                    shade: Math.floor(Math.random() * 3)
                };
            });
        }

        // A double "lub-dub" thump once per beat
        function beat(ms) {
            const phase = (ms / (60000 / BPM)) % 1;
            const thump = (at, strength) => strength * Math.exp(-Math.pow((phase - at) / 0.055, 2));
            return 1 + thump(0.12, 0.09) + thump(0.34, 0.05);
        }

        function draw(ms, still) {
            const dark = document.documentElement.dataset.theme === 'dark';
            const colors = dark ? ['#4CAF50', '#8BD493', '#D3F5D6'] : ['#1B5E20', '#2E7D32', '#4CAF50'];
            const scale = still ? 1 : beat(ms);
            const reach = size * 0.17;
            ctx.clearRect(0, 0, size, size);

            for (let shade = 0; shade < 3; shade++) {
                ctx.fillStyle = colors[shade];
                ctx.beginPath();
                for (const p of particles) {
                    if (p.shade !== shade) continue;
                    if (still) {
                        p.x = p.hx; p.y = p.hy;
                    } else {
                        // Spring towards home, pushed away by the pointer
                        p.vx += (p.hx * scale - p.x) * 0.025;
                        p.vy += (p.hy * scale - p.y) * 0.025;
                        const dx = p.x - pointer.x;
                        const dy = p.y - pointer.y;
                        const dist = Math.hypot(dx, dy);
                        if (dist < reach && dist > 0.1) {
                            const push = (1 - dist / reach) * 5;
                            p.vx += (dx / dist) * push;
                            p.vy += (dy / dist) * push;
                        }
                        p.vx *= 0.84; p.vy *= 0.84;
                        p.x += p.vx; p.y += p.vy;
                    }
                    const x = p.x + size / 2;
                    const y = p.y + size / 2 - size * 0.03;
                    ctx.moveTo(x + p.r, y);
                    ctx.arc(x, y, p.r, 0, Math.PI * 2);
                }
                ctx.fill();
            }
        }

        function loop(ms) {
            draw(ms, false);
            frame = requestAnimationFrame(loop);
        }

        // Animate only when visible and motion is allowed
        function sync() {
            cancelAnimationFrame(frame);
            if (reduced.matches) draw(0, true);
            else if (onScreen && !document.hidden) frame = requestAnimationFrame(loop);
        }

        function locate(e) {
            const box = canvas.getBoundingClientRect();
            pointer.x = e.clientX - box.left - size / 2;
            pointer.y = e.clientY - box.top - size / 2 + size * 0.03;
        }
        const release = () => { pointer.x = pointer.y = -9999; };

        canvas.addEventListener('pointermove', locate);
        canvas.addEventListener('pointerleave', release);
        canvas.addEventListener('pointercancel', release);
        canvas.addEventListener('pointerup', e => { if (e.pointerType !== 'mouse') release(); });
        canvas.addEventListener('pointerdown', e => {
            locate(e);
            if (reduced.matches) return;
            for (const p of particles) {
                const angle = Math.atan2(p.y - pointer.y, p.x - pointer.x);
                const force = 6 + Math.random() * 14;
                p.vx += Math.cos(angle) * force;
                p.vy += Math.sin(angle) * force;
            }
        });

        let lastWidth = 0;
        new ResizeObserver(() => {
            if (canvas.clientWidth === lastWidth) return;
            lastWidth = canvas.clientWidth;
            build();
            sync();
        }).observe(canvas);

        new IntersectionObserver(([entry]) => {
            onScreen = entry.isIntersecting;
            sync();
        }).observe(canvas);

        document.addEventListener('visibilitychange', sync);
        reduced.addEventListener('change', sync);
        new MutationObserver(() => { if (reduced.matches) draw(0, true); })
            .observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
    }

    // ─── Scroll progress and pinned story ─────────────────────────
    function scrollEffects() {
        const bar = document.querySelector('.lp-progress');
        const story = document.querySelector('.lp-story');
        const steps = story ? [...story.querySelectorAll('.lp-step')] : [];
        // Pinning needs enough height for the whole stage
        const roomy = window.matchMedia('(min-height: 620px)');
        const clamp = v => Math.min(1, Math.max(0, v));
        let queued = false;

        function update() {
            queued = false;
            const max = document.documentElement.scrollHeight - window.innerHeight;
            if (bar) bar.style.transform = `scaleX(${max > 0 ? clamp(window.scrollY / max) : 0})`;
            if (!story || !story.classList.contains('story-on')) return;

            const box = story.getBoundingClientRect();
            const progress = clamp(-box.top / (box.height - window.innerHeight));
            const active = Math.min(steps.length - 1, Math.floor(progress * steps.length));
            steps.forEach((step, i) => {
                step.classList.toggle('is-active', i === active);
                step.classList.toggle('is-past', i < active);
            });
            story.style.setProperty('--story', progress.toFixed(3));
            // The chart draws during the middle third
            const draw = clamp((progress - 0.34) / 0.28);
            story.style.setProperty('--draw', draw.toFixed(3));
            story.style.setProperty('--dot', draw > 0.97 ? 1 : 0);
        }

        function request() {
            if (!queued) {
                queued = true;
                requestAnimationFrame(update);
            }
        }

        function mode() {
            if (!story) return;
            const on = !reduced.matches && roomy.matches;
            story.classList.toggle('story-on', on);
            if (!on) ['--story', '--draw', '--dot'].forEach(v => story.style.removeProperty(v));
            update();
        }

        window.addEventListener('scroll', request, { passive: true });
        window.addEventListener('resize', request);
        reduced.addEventListener('change', mode);
        roomy.addEventListener('change', mode);
        mode();
    }

    // ─── Reveal on scroll ─────────────────────────────────────────
    function reveals() {
        const observer = new IntersectionObserver(entries => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('is-in');
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.15 });
        document.querySelectorAll('.lp-reveal').forEach(el => observer.observe(el));
    }

    // ─── Flip cards (click, tap, Enter or Space) ──────────────────
    function flipCards() {
        document.querySelectorAll('.flip-card').forEach(card => {
            card.addEventListener('click', () => {
                const flipped = card.getAttribute('aria-pressed') !== 'true';
                card.setAttribute('aria-pressed', String(flipped));
                card.querySelector('.flip-face--front').setAttribute('aria-hidden', String(flipped));
                card.querySelector('.flip-face--back').setAttribute('aria-hidden', String(!flipped));
            });
        });
    }

    document.addEventListener('DOMContentLoaded', () => {
        const canvas = document.getElementById('heartCanvas');
        if (canvas) particleHeart(canvas);
        scrollEffects();
        reveals();
        flipCards();
    });
})();
