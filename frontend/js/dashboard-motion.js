/**
 * Dashboard motion: Living Pulse trace, number count-up, save animation,
 * guided breathing and chat open/close. No external libraries.
 */
(function () {
    'use strict';

    const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');

    // ─── Living Pulse ─────────────────────────────────────────────
    const IDLE_BPM = 50;
    const SECONDS_SHOWN = 4;
    const pulse = { bpm: 0, frame: 0, onScreen: true };
    let banner, canvas, ctx, width = 0, height = 0;

    // One heartbeat as a function of seconds since it began (P, Q, R, S, T waves)
    function ecg(t) {
        const wave = (at, wide, tall) => tall * Math.exp(-Math.pow((t - at) / wide, 2));
        return wave(0.10, 0.025, 0.12) - wave(0.19, 0.010, 0.18) + wave(0.22, 0.012, 1)
            - wave(0.25, 0.012, 0.28) + wave(0.42, 0.045, 0.24);
    }

    function draw(seconds) {
        if (!width) return;
        const idle = !pulse.bpm;
        const period = 60 / (pulse.bpm || IDLE_BPM);
        const tone = getComputedStyle(banner).getPropertyValue('--tone').trim();
        ctx.clearRect(0, 0, width, height);
        ctx.beginPath();
        for (let x = 0; x <= width; x += 1.5) {
            const t = seconds - SECONDS_SHOWN * (1 - x / width);
            const phase = ((t % period) + period) % period;
            const value = idle ? 0.08 * Math.sin(t * 3) : ecg(phase);
            const y = height * 0.68 - value * height * 0.55;
            if (x === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
        }
        const fade = ctx.createLinearGradient(0, 0, width, 0);
        fade.addColorStop(0, 'transparent');
        fade.addColorStop(0.5, tone);
        fade.addColorStop(1, tone);
        ctx.strokeStyle = fade;
        ctx.lineWidth = 2.5;
        ctx.lineJoin = 'round';
        ctx.stroke();

        // Heart and glow thump as the R wave reaches the right-hand edge
        const now = ((seconds % period) + period) % period;
        const thump = idle || reduced.matches ? 0 : Math.exp(-Math.pow((now - 0.22) / 0.09, 2));
        banner.style.setProperty('--thump', thump.toFixed(3));
    }

    function loop(ms) {
        draw(ms / 1000);
        pulse.frame = requestAnimationFrame(loop);
    }

    function sync() {
        cancelAnimationFrame(pulse.frame);
        if (!banner) return;
        if (reduced.matches) draw(SECONDS_SHOWN);
        else if (pulse.onScreen && !document.hidden) pulse.frame = requestAnimationFrame(loop);
    }

    function resize() {
        width = canvas.clientWidth;
        height = canvas.clientHeight;
        const ratio = Math.min(window.devicePixelRatio || 1, 2);
        canvas.width = width * ratio;
        canvas.height = height * ratio;
        ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
        sync();
    }

    function setText(id, text) {
        document.getElementById(id).textContent = text;
    }

    /** record: latest reading, null for no readings, or 'error' if loading failed */
    function updatePulse(record) {
        if (!banner) return;
        const failed = record === 'error';
        const bpm = !failed && record && record.heart_rate > 0 ? record.heart_rate : 0;
        pulse.bpm = Math.min(bpm, 220);
        let state = 'idle';
        let label = failed ? 'Could not load your readings' : 'Add your first reading';
        if (bpm) {
            state = bpm >= 60 && bpm <= 100 ? 'ok' : 'warn';
            label = bpm < 60 ? 'Below 60–100 bpm range'
                : bpm > 100 ? 'Above 60–100 bpm range' : 'Within 60–100 bpm range';
        }
        banner.dataset.state = state;
        setText('pulseBpm', bpm || '--');
        setText('pulseLabel', label);
        document.getElementById('pulseAction').hidden = Boolean(bpm) || failed;
        canvas.setAttribute('aria-label', bpm
            ? `Illustrated pulse beating at your latest heart rate, ${bpm} beats per minute`
            : 'No heart rate reading to show');
        sync();
    }

    // ─── Count up ─────────────────────────────────────────────────
    const counting = new WeakMap();

    function countTo(el, value, format) {
        if (!el) return;
        cancelAnimationFrame(counting.get(el));
        if (reduced.matches || document.hidden) {
            el.textContent = format(value);
            return;
        }
        const start = performance.now();
        const step = now => {
            const p = Math.min(1, Math.max(0, (now - start) / 900));
            el.textContent = format(value * (1 - Math.pow(1 - p, 3)));
            if (p < 1) counting.set(el, requestAnimationFrame(step));
        };
        counting.set(el, requestAnimationFrame(step));
    }

    // ─── Saved reading flies into its card ────────────────────────
    function celebrateSave(fromBox) {
        const card = document.getElementById('statHeartRate');
        if (!card || !fromBox || reduced.matches || !card.animate) return;
        card.scrollIntoView({ block: 'nearest' });
        const to = card.getBoundingClientRect();
        const ghost = document.createElement('div');
        ghost.className = 'save-ghost';
        document.body.appendChild(ghost);
        const frame = (b, opacity) => ({
            left: `${b.left}px`, top: `${b.top}px`, width: `${b.width}px`, height: `${b.height}px`, opacity
        });
        const flight = ghost.animate([frame(fromBox, 0.9), frame(to, 0.35)],
            { duration: 650, easing: 'cubic-bezier(0.22, 1, 0.36, 1)', fill: 'forwards' });
        const land = () => {
            ghost.remove();
            card.classList.remove('just-saved');
            void card.offsetWidth; // restart the glow
            card.classList.add('just-saved');
            setTimeout(() => card.classList.remove('just-saved'), 3000);
        };
        flight.onfinish = land;
        flight.oncancel = land;
    }

    // ─── Guided breathing, driven by the wellness timer ───────────
    const PHASES = [
        { name: 'Breathe in', seconds: 4, scale: 1 },
        { name: 'Hold', seconds: 4, scale: 1 },
        { name: 'Breathe out', seconds: 6, scale: 0.55 }
    ];
    const CYCLE = PHASES.reduce((sum, p) => sum + p.seconds, 0);

    function breathe(running, elapsed) {
        const circle = document.querySelector('.breath-circle');
        const text = document.querySelector('.breath-text');
        if (!circle || !text) return;
        if (!running) {
            // Freeze where it is when paused; shrink back on reset
            const current = getComputedStyle(circle).transform;
            circle.style.transitionDuration = '0s';
            circle.style.transform = elapsed ? current : 'scale(0.55)';
            text.textContent = elapsed ? 'Paused' : 'Press play';
            return;
        }
        let into = elapsed % CYCLE;
        const phase = PHASES.find(p => {
            if (into < p.seconds) return true;
            into -= p.seconds;
            return false;
        });
        const target = `scale(${phase.scale})`;
        if (text.textContent !== phase.name || circle.style.transform !== target) {
            circle.style.transitionDuration = `${phase.seconds - into}s`;
            circle.style.transform = target;
            text.textContent = phase.name;
        }
    }

    // ─── Chat button morphs into the window ───────────────────────
    let chatOpen = false;
    let chatAnimation = null;

    function toggleChat() {
        const chat = document.getElementById('chatbot-container');
        const button = document.getElementById('chatbot-toggle');
        chatOpen = !chatOpen;
        if (chatAnimation) chatAnimation.cancel();
        if (chatOpen) {
            chat.style.display = 'flex';
            button.style.display = 'none';
        }
        const finish = () => {
            if (!chatOpen) {
                chat.style.display = 'none';
                button.style.display = 'flex';
            } else {
                document.getElementById('chatInput').focus({ preventScroll: true });
            }
        };
        if (reduced.matches || !chat.animate) {
            finish();
            return;
        }
        const closed = { transform: 'translateY(40px) scale(0.12)', borderRadius: '50%', opacity: 0 };
        const open = { transform: 'none', borderRadius: getComputedStyle(chat).borderRadius, opacity: 1 };
        chatAnimation = chat.animate(chatOpen ? [closed, open] : [open, closed], {
            duration: chatOpen ? 450 : 260,
            easing: chatOpen ? 'cubic-bezier(0.34, 1.4, 0.64, 1)' : 'ease-in'
        });
        chatAnimation.onfinish = finish;
    }

    // ─── Start ────────────────────────────────────────────────────
    document.addEventListener('DOMContentLoaded', () => {
        banner = document.getElementById('livingPulse');
        canvas = document.getElementById('pulseTrace');
        ctx = canvas && canvas.getContext('2d');
        if (!ctx) { banner = null; return; }
        new ResizeObserver(resize).observe(canvas);
        new IntersectionObserver(([entry]) => {
            pulse.onScreen = entry.isIntersecting;
            sync();
        }).observe(banner);
        document.addEventListener('visibilitychange', sync);
        reduced.addEventListener('change', sync);
        new MutationObserver(sync).observe(document.documentElement,
            { attributes: true, attributeFilter: ['data-theme'] });
    });

    window.dashboardMotion = { updatePulse, countTo, celebrateSave, breathe, toggleChat };
})();
