/**
 * HealthAI motion layer: theme switch, tilt, magnetic buttons, ripple,
 * loading skeletons and toasts. No external libraries.
 * Load in <head> so the saved theme applies before the page is drawn.
 */
(function () {
    'use strict';

    const root = document.documentElement;
    const THEME_KEY = 'healthai-theme';
    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
    const darkPreference = window.matchMedia('(prefers-color-scheme: dark)');
    const finePointer = window.matchMedia('(hover: hover) and (pointer: fine)');

    // ─── Theme ────────────────────────────────────────────────────
    function savedTheme() {
        try { return localStorage.getItem(THEME_KEY); } catch (e) { return null; }
    }

    const ICONS = {
        // Shown in light mode (switch to dark)
        light: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg>',
        // Shown in dark mode (switch to light)
        dark: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>'
    };

    let themeButton = null;

    function applyTheme(theme) {
        root.setAttribute('data-theme', theme);
        if (themeButton) {
            themeButton.innerHTML = ICONS[theme];
            const label = theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode';
            themeButton.setAttribute('aria-label', label);
            themeButton.title = label;
        }
        styleCharts();
    }

    function styleCharts() {
        if (!window.Chart) return;
        const css = getComputedStyle(root);
        window.Chart.defaults.color = css.getPropertyValue('--text-secondary').trim();
        window.Chart.defaults.borderColor = css.getPropertyValue('--border-color').trim();
        Object.values(window.Chart.instances || {}).forEach(chart => chart.update('none'));
    }

    function toggleTheme(event) {
        const next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
        try { localStorage.setItem(THEME_KEY, next); } catch (e) { /* storage blocked */ }

        if (!document.startViewTransition || reducedMotion.matches) {
            applyTheme(next);
            return;
        }
        const box = event.currentTarget.getBoundingClientRect();
        root.style.setProperty('--fx-x', `${box.left + box.width / 2}px`);
        root.style.setProperty('--fx-y', `${box.top + box.height / 2}px`);
        document.startViewTransition(() => applyTheme(next));
    }

    applyTheme(savedTheme() || (darkPreference.matches ? 'dark' : 'light'));
    darkPreference.addEventListener('change', e => {
        if (!savedTheme()) applyTheme(e.matches ? 'dark' : 'light');
    });

    function addThemeButton() {
        themeButton = document.createElement('button');
        themeButton.type = 'button';
        themeButton.className = 'fx-theme-btn';
        themeButton.addEventListener('click', toggleTheme);

        const topbar = document.querySelector('.topbar-actions');
        const landingNav = document.querySelector('.landing-nav');
        if (topbar) {
            topbar.prepend(themeButton);
        } else if (landingNav) {
            themeButton.classList.add('fx-theme-btn--nav');
            landingNav.appendChild(themeButton);
        } else {
            themeButton.classList.add('fx-theme-btn--floating');
            document.body.appendChild(themeButton);
        }
        applyTheme(root.getAttribute('data-theme'));
    }

    // ─── Card tilt and magnetic buttons (mouse only) ──────────────
    const TILT = '.stat-card, .landing-feature-card, .hero-card-preview, .edu-card';
    const MAGNETIC = '.page-header .btn, .landing-hero-buttons .btn, .auth-submit-btn';

    function followPointer(selector, className, onMove, onLeave) {
        document.querySelectorAll(selector).forEach(el => {
            el.classList.add(className);
            let frame = 0;
            el.addEventListener('pointermove', e => {
                if (!finePointer.matches || reducedMotion.matches) return;
                cancelAnimationFrame(frame);
                frame = requestAnimationFrame(() => {
                    const b = el.getBoundingClientRect();
                    // -0.5 … 0.5 from the centre of the element
                    onMove(el, (e.clientX - b.left) / b.width - 0.5, (e.clientY - b.top) / b.height - 0.5);
                });
            });
            el.addEventListener('pointerleave', () => {
                cancelAnimationFrame(frame);
                onLeave(el);
            });
        });
    }

    function addPointerEffects() {
        followPointer(TILT, 'fx-tilt', (el, x, y) => {
            el.style.setProperty('--fx-rx', `${(-y * 8).toFixed(2)}deg`);
            el.style.setProperty('--fx-ry', `${(x * 8).toFixed(2)}deg`);
            el.classList.add('fx-tilting');
        }, el => el.classList.remove('fx-tilting'));

        followPointer(MAGNETIC, 'fx-magnetic', (el, x, y) => {
            el.style.setProperty('--fx-mx', `${(x * 10).toFixed(1)}px`);
            el.style.setProperty('--fx-my', `${(y * 8).toFixed(1)}px`);
        }, el => {
            el.style.removeProperty('--fx-mx');
            el.style.removeProperty('--fx-my');
        });
    }

    // ─── Click ripple ─────────────────────────────────────────────
    const RIPPLE = 'button, .btn, .sidebar-link, .nav-btn-login, .nav-btn-signup';

    document.addEventListener('pointerdown', e => {
        const target = e.target.closest && e.target.closest(RIPPLE);
        if (!target || target.disabled || reducedMotion.matches) return;

        // Drawn as an overlay, so the button's own layout is never changed
        const box = target.getBoundingClientRect();
        const layer = document.createElement('div');
        layer.className = 'fx-ripple';
        layer.style.cssText = `left:${box.left}px;top:${box.top}px;width:${box.width}px;height:${box.height}px;border-radius:${getComputedStyle(target).borderRadius}`;
        const size = Math.hypot(box.width, box.height) * 2;
        const wave = document.createElement('span');
        wave.style.cssText = `width:${size}px;height:${size}px;left:${e.clientX - box.left - size / 2}px;top:${e.clientY - box.top - size / 2}px`;
        layer.appendChild(wave);
        document.body.appendChild(layer);
        setTimeout(() => layer.remove(), 650);
    });

    // ─── Loading skeletons ────────────────────────────────────────
    // Shown while API requests are in flight.
    const SKELETON = '.stat-value, #healthChart, .data-table, #reportsList';
    let pending = 0;
    let settleTimer = 0;

    function clearSkeletons() {
        document.querySelectorAll('.fx-skeleton').forEach(el => {
            el.classList.remove('fx-skeleton');
            el.removeAttribute('aria-busy');
        });
    }

    function settle() {
        clearTimeout(settleTimer);
        settleTimer = setTimeout(() => { if (pending === 0) clearSkeletons(); }, 250);
    }

    const nativeFetch = window.fetch.bind(window);
    window.fetch = function (...args) {
        pending++;
        return nativeFetch(...args).finally(() => { pending--; settle(); });
    };

    function addSkeletons() {
        if (!document.querySelector('.app-layout')) return;
        document.querySelectorAll(SKELETON).forEach(el => {
            el.classList.add('fx-skeleton');
            el.setAttribute('aria-busy', 'true');
        });
        settle();
        setTimeout(clearSkeletons, 8000); // never hide content for long
    }

    // ─── Toast notifications ──────────────────────────────────────
    const TOAST_ICONS = { success: '✓', error: '!', warning: '!', info: 'i' };

    function toast(message, type = 'info', duration = 3000) {
        let stack = document.querySelector('.fx-toasts');
        if (!stack) {
            stack = document.createElement('div');
            stack.className = 'fx-toasts';
            stack.setAttribute('role', 'status');
            stack.setAttribute('aria-live', 'polite');
            document.body.appendChild(stack);
        }
        const item = document.createElement('div');
        item.className = `fx-toast fx-toast--${type}`;
        item.style.setProperty('--fx-life', `${duration}ms`);
        const icon = document.createElement('span');
        icon.className = 'fx-toast-icon';
        icon.setAttribute('aria-hidden', 'true');
        icon.textContent = TOAST_ICONS[type] || 'i';
        const text = document.createElement('span');
        text.textContent = message;
        item.append(icon, text);
        stack.appendChild(item);
        setTimeout(() => {
            item.classList.add('fx-leaving');
            setTimeout(() => item.remove(), 300);
        }, duration);
    }

    // ─── Start ────────────────────────────────────────────────────
    document.addEventListener('visibilitychange', () => {
        root.classList.toggle('fx-paused', document.hidden);
    });

    document.addEventListener('DOMContentLoaded', () => {
        addThemeButton();
        addPointerEffects();
        addSkeletons();
    });

    window.healthMotion = { toast };
})();
