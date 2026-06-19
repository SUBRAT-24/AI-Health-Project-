/**
 * API Configuration - Central config for all frontend API calls
 * 
 * This file MUST be loaded BEFORE main.js, admin.js, chatbot.js, etc.
 * It sets the global API_BASE_URL used by all JavaScript files.
 * 
 * For local development: points to localhost:5000
 * For production (Vercel → Render): points to your Render backend URL
 */

(function () {
    'use strict';

    // ─── PRODUCTION BACKEND URL ─────────────────────────────────────────────────
    // Replace this with your actual Render backend URL after deploying
    // Example: 'https://ai-health-assistant-backend.onrender.com'
    const RENDER_BACKEND_URL = 'https://ai-health-project-t1es.onrender.com';
    // ────────────────────────────────────────────────────────────────────────────

    function getApiBaseUrl() {
        const hostname = window.location.hostname;

        // Local development
        if (hostname === 'localhost' || hostname === '127.0.0.1') {
            return window.location.origin + '/api';
        }

        // Production (Vercel or any deployed frontend)
        if (RENDER_BACKEND_URL && RENDER_BACKEND_URL !== 'YOUR_RENDER_BACKEND_URL') {
            return RENDER_BACKEND_URL.replace(/\/+$/, '') + '/api';
        }

        // Fallback: assume same origin (won't work for cross-origin but prevents crash)
        console.warn('[API Config] RENDER_BACKEND_URL not set! Update frontend/js/api-config.js');
        return window.location.origin + '/api';
    }

    // Set the global variable used by all JS files
    window.API_BASE_URL = getApiBaseUrl();

    console.log('[API Config] API_BASE_URL =', window.API_BASE_URL);
})();
