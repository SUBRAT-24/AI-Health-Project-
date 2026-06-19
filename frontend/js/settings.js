/**
 * Settings Page JavaScript
 * Handles profile, preferences, notifications, privacy & personalization
 */

document.addEventListener('DOMContentLoaded', function () {
    if (!window.healthAssistant.isAuthenticated()) {
        window.location.href = 'login.html';
        return;
    }
    populateUserBar();
    loadProfile();
    loadPreferences();
    loadEmailVerificationStatus();
});

function populateUserBar() {
    const userName = localStorage.getItem('userName') || 'User';
    const userData = JSON.parse(localStorage.getItem('userData') || '{}');
    const el = (id) => document.getElementById(id);
    if (el('topbarUserName')) el('topbarUserName').textContent = userName;
    if (el('topbarUserEmail')) el('topbarUserEmail').textContent = userData.email || '';
    if (el('userAvatar')) el('userAvatar').textContent = userName.charAt(0).toUpperCase();
}

// ─── TAB SWITCHING ──────────────────────────────────────────────────────────────

function switchSettingsTab(tab) {
    document.querySelectorAll('.settings-tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.settings-panel').forEach(p => p.classList.remove('active'));
    document.querySelector(`.settings-tab[data-tab="${tab}"]`).classList.add('active');
    document.getElementById('panel-' + tab).classList.add('active');
}

// ─── LOAD PROFILE ───────────────────────────────────────────────────────────────

async function loadProfile() {
    try {
        const data = await window.healthAssistant.apiRequest('/settings/profile');
        if (!data) return;

        const el = (id) => document.getElementById(id);
        if (el('settName')) el('settName').value = data.name || '';
        if (el('settEmail')) el('settEmail').value = data.email || '';
        if (el('settPhone')) el('settPhone').value = data.phone || '';
        if (el('settDob') && data.date_of_birth) el('settDob').value = data.date_of_birth;
        if (el('settGender')) el('settGender').value = data.gender || 'male';
        if (el('settBloodType')) el('settBloodType').value = data.blood_type || '';
        if (el('settHeight')) el('settHeight').value = data.height || '';
        if (el('settEmName')) el('settEmName').value = data.emergency_contact_name || '';
        if (el('settEmPhone')) el('settEmPhone').value = data.emergency_contact_phone || '';
        if (el('settAllergies')) el('settAllergies').value = data.allergies || '';
        if (el('settMedHistory')) el('settMedHistory').value = data.medical_history || '';

        if (el('accountCreated') && data.created_at) {
            el('accountCreated').textContent = new Date(data.created_at).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
        }
        if (el('accountUpdated') && data.updated_at) {
            el('accountUpdated').textContent = new Date(data.updated_at).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
        }
        if (el('accountRole')) el('accountRole').textContent = (data.role || 'user').charAt(0).toUpperCase() + (data.role || 'user').slice(1);
    } catch (e) {
        console.error('Failed to load profile:', e);
    }
}

// ─── SAVE PROFILE ───────────────────────────────────────────────────────────────

async function saveProfile() {
    const el = (id) => document.getElementById(id);
    try {
        await window.healthAssistant.apiRequest('/settings/profile', 'PUT', {
            name: el('settName').value,
            phone: el('settPhone').value,
            date_of_birth: el('settDob').value,
            gender: el('settGender').value,
            blood_type: el('settBloodType').value,
            height: parseFloat(el('settHeight').value) || null,
            allergies: el('settAllergies').value,
            medical_history: el('settMedHistory').value,
            emergency_contact_name: el('settEmName').value,
            emergency_contact_phone: el('settEmPhone').value,
        });
        window.healthAssistant.showToast('Profile saved successfully!', 'success');
        if (el('settName').value) {
            localStorage.setItem('userName', el('settName').value);
            populateUserBar();
        }
    } catch (e) {
        window.healthAssistant.showToast('Failed to save profile', 'error');
    }
}

// ─── LOAD PREFERENCES ──────────────────────────────────────────────────────────

async function loadPreferences() {
    try {
        const prefs = await window.healthAssistant.apiRequest('/settings/preferences');
        if (!prefs) return;
        const el = (id) => document.getElementById(id);

        // Health thresholds
        if (el('thrHrMin')) el('thrHrMin').value = prefs.hr_min ?? 60;
        if (el('thrHrMax')) el('thrHrMax').value = prefs.hr_max ?? 100;
        if (el('thrBpSysMin')) el('thrBpSysMin').value = prefs.bp_sys_min ?? 90;
        if (el('thrBpSysMax')) el('thrBpSysMax').value = prefs.bp_sys_max ?? 140;
        if (el('thrBpDiaMin')) el('thrBpDiaMin').value = prefs.bp_dia_min ?? 60;
        if (el('thrBpDiaMax')) el('thrBpDiaMax').value = prefs.bp_dia_max ?? 90;
        if (el('thrTempMin')) el('thrTempMin').value = prefs.temp_min ?? 36.0;
        if (el('thrTempMax')) el('thrTempMax').value = prefs.temp_max ?? 37.5;

        // Goals
        if (el('goalSteps')) el('goalSteps').value = prefs.daily_steps_goal ?? 10000;
        if (el('goalWater')) el('goalWater').value = prefs.daily_water_goal ?? 8;
        if (el('goalSleep')) el('goalSleep').value = prefs.daily_sleep_goal ?? 8;

        // Units & notifications
        if (el('settUnits')) el('settUnits').value = prefs.measurement_units || 'metric';
        if (el('toggleVitalAlerts')) el('toggleVitalAlerts').checked = prefs.vital_alerts_enabled !== false;
        if (el('alertFreq')) el('alertFreq').value = prefs.alert_frequency || 'immediate';
        if (el('notifMethod')) el('notifMethod').value = prefs.notification_method || 'dashboard';
        if (el('aptReminder')) el('aptReminder').value = prefs.appointment_reminder || '24h';
        if (el('toggleMedReminder')) el('toggleMedReminder').checked = prefs.medicine_reminder !== false;

        // Preferences
        if (el('toggleDarkMode')) el('toggleDarkMode').checked = prefs.theme === 'dark';
        if (el('settLang')) el('settLang').value = prefs.language || 'en';
        if (el('settDateFmt')) el('settDateFmt').value = prefs.date_format || 'DD/MM/YYYY';
        if (el('settTimezone')) el('settTimezone').value = prefs.timezone || 'Asia/Kolkata';
        if (el('settDiet')) el('settDiet').value = prefs.dietary_preference || 'non-veg';
        if (el('settFitness')) el('settFitness').value = prefs.fitness_level || 'moderate';
    } catch (e) {
        console.error('Failed to load preferences:', e);
    }
}

// ─── SAVE FUNCTIONS ─────────────────────────────────────────────────────────────

function gatherPrefs() {
    const el = (id) => document.getElementById(id);
    return {
        hr_min: parseInt(el('thrHrMin')?.value) || 60,
        hr_max: parseInt(el('thrHrMax')?.value) || 100,
        bp_sys_min: parseInt(el('thrBpSysMin')?.value) || 90,
        bp_sys_max: parseInt(el('thrBpSysMax')?.value) || 140,
        bp_dia_min: parseInt(el('thrBpDiaMin')?.value) || 60,
        bp_dia_max: parseInt(el('thrBpDiaMax')?.value) || 90,
        temp_min: parseFloat(el('thrTempMin')?.value) || 36.0,
        temp_max: parseFloat(el('thrTempMax')?.value) || 37.5,
        daily_steps_goal: parseInt(el('goalSteps')?.value) || 10000,
        daily_water_goal: parseInt(el('goalWater')?.value) || 8,
        daily_sleep_goal: parseInt(el('goalSleep')?.value) || 8,
        measurement_units: el('settUnits')?.value || 'metric',
        vital_alerts_enabled: el('toggleVitalAlerts')?.checked ?? true,
        alert_frequency: el('alertFreq')?.value || 'immediate',
        notification_method: el('notifMethod')?.value || 'dashboard',
        appointment_reminder: el('aptReminder')?.value || '24h',
        medicine_reminder: el('toggleMedReminder')?.checked ?? true,
        theme: el('toggleDarkMode')?.checked ? 'dark' : 'light',
        language: el('settLang')?.value || 'en',
        date_format: el('settDateFmt')?.value || 'DD/MM/YYYY',
        timezone: el('settTimezone')?.value || 'Asia/Kolkata',
        dietary_preference: el('settDiet')?.value || 'non-veg',
        fitness_level: el('settFitness')?.value || 'moderate',
    };
}

async function saveHealthPreferences() {
    try {
        await window.healthAssistant.apiRequest('/settings/preferences', 'PUT', gatherPrefs());
        window.healthAssistant.showToast('Health preferences saved!', 'success');
    } catch (e) { window.healthAssistant.showToast('Failed to save', 'error'); }
}

async function saveNotificationSettings() {
    try {
        await window.healthAssistant.apiRequest('/settings/preferences', 'PUT', gatherPrefs());
        window.healthAssistant.showToast('Notification settings saved!', 'success');
    } catch (e) { window.healthAssistant.showToast('Failed to save', 'error'); }
}

async function savePreferences() {
    try {
        await window.healthAssistant.apiRequest('/settings/preferences', 'PUT', gatherPrefs());
        window.healthAssistant.showToast('Preferences saved!', 'success');
    } catch (e) { window.healthAssistant.showToast('Failed to save', 'error'); }
}

async function saveAllSettings() {
    await saveProfile();
    try {
        await window.healthAssistant.apiRequest('/settings/preferences', 'PUT', gatherPrefs());
    } catch (e) {}
    window.healthAssistant.showToast('All settings saved!', 'success');
}

// ─── PASSWORD CHANGE ────────────────────────────────────────────────────────────

async function changePassword() {
    const el = (id) => document.getElementById(id);
    const cur = el('currentPass').value;
    const nw = el('newPass').value;
    const conf = el('confirmNewPass').value;
    if (!cur || !nw || !conf) return window.healthAssistant.showToast('All password fields are required', 'error');
    if (nw !== conf) return window.healthAssistant.showToast('New passwords do not match', 'error');
    if (nw.length < 6) return window.healthAssistant.showToast('Password must be at least 6 characters', 'error');
    try {
        await window.healthAssistant.apiRequest('/settings/change-password', 'POST', { current_password: cur, new_password: nw });
        window.healthAssistant.showToast('Password changed successfully!', 'success');
        el('currentPass').value = '';
        el('newPass').value = '';
        el('confirmNewPass').value = '';
    } catch (e) {}
}

// ─── DATA EXPORT ────────────────────────────────────────────────────────────────

async function exportAllData() {
    try {
        const data = await window.healthAssistant.apiRequest('/settings/export-data');
        if (!data) return;
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `healthai_data_export_${new Date().toISOString().split('T')[0]}.json`;
        a.click();
        URL.revokeObjectURL(url);
        window.healthAssistant.showToast('Data exported successfully!', 'success');
    } catch (e) { window.healthAssistant.showToast('Export failed', 'error'); }
}

// ─── ACCOUNT DELETION ───────────────────────────────────────────────────────────

async function requestAccountDeletion() {
    const password = prompt('Enter your password to confirm account deletion:');
    if (!password) return;
    if (!confirm('Are you sure? This action will deactivate your account.')) return;
    try {
        await window.healthAssistant.apiRequest('/settings/delete-account', 'DELETE', { password });
        window.healthAssistant.showToast('Account deactivated. You will be logged out.', 'info');
        setTimeout(() => window.healthAssistant.logoutUser(), 2000);
    } catch (e) {}
}

// ─── EMAIL VERIFICATION ─────────────────────────────────────────────────────────

async function loadEmailVerificationStatus() {
    try {
        const data = await window.healthAssistant.apiRequest('/settings/profile');
        if (!data) return;
        const badge = document.getElementById('verifyBadge');
        const step1 = document.getElementById('verifyStep1');
        const step2 = document.getElementById('verifyStep2');
        const done = document.getElementById('verifyDone');
        const desc = document.getElementById('verifyDesc');

        if (data.email_verified) {
            if (badge) { badge.className = 'verification-badge verified'; badge.innerHTML = '<span class="verify-icon">✅</span><span class="verify-text">Email verified</span>'; }
            if (step1) step1.style.display = 'none';
            if (step2) step2.style.display = 'none';
            if (done) done.style.display = 'block';
            if (desc) desc.textContent = 'Your email address has been verified.';
        }

        // Auto-fill the reset email field
        const resetEmail = document.getElementById('resetEmail');
        if (resetEmail && data.email) resetEmail.value = data.email;
    } catch (e) {
        console.error('Failed to load verification status:', e);
    }
}

async function sendVerificationCode() {
    const btn = document.getElementById('sendCodeBtn');
    if (btn) { btn.disabled = true; btn.textContent = 'Sending...'; }
    try {
        const res = await window.healthAssistant.apiRequest('/settings/send-verification-code', 'POST');
        if (!res) return;

        // Show step 2
        const step1 = document.getElementById('verifyStep1');
        const step2 = document.getElementById('verifyStep2');
        const hint = document.getElementById('verifyHint');
        if (step1) step1.style.display = 'none';
        if (step2) step2.style.display = 'block';
        if (hint) hint.innerHTML = res.hint ? res.hint : res.message;

        window.healthAssistant.showToast(res.message || 'Verification code sent!', 'success');
    } catch (e) {
        window.healthAssistant.showToast('Failed to send code', 'error');
    } finally {
        if (btn) { btn.disabled = false; btn.textContent = '📩 Send Verification Code'; }
    }
}

async function verifyEmailCode() {
    const code = document.getElementById('verifyCodeInput')?.value.trim();
    if (!code || code.length !== 6) {
        return window.healthAssistant.showToast('Please enter the 6-digit code', 'error');
    }
    try {
        const res = await window.healthAssistant.apiRequest('/settings/verify-email', 'POST', { code });
        if (res && (res.message || '').toLowerCase().includes('verified')) {
            window.healthAssistant.showToast('Email verified successfully!', 'success');
            loadEmailVerificationStatus(); // Refresh the UI
        }
    } catch (e) {}
}

// ─── PASSWORD RESET (from Settings) ─────────────────────────────────────────────

async function requestPasswordReset() {
    const email = document.getElementById('resetEmail')?.value.trim();
    if (!email) return window.healthAssistant.showToast('Please enter your email', 'error');
    try {
        const res = await window.healthAssistant.apiRequest('/settings/request-password-reset', 'POST', { email });
        const hint = document.getElementById('resetHint');
        if (hint && res) {
            hint.style.display = 'block';
            hint.innerHTML = res.hint ? res.hint : res.message;
        }
        window.healthAssistant.showToast(res?.message || 'Reset link sent!', 'success');
    } catch (e) {
        window.healthAssistant.showToast('Failed to send reset link', 'error');
    }
}
