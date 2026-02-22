/**
 * Admin panel - API and UI helpers
 */
const API_BASE_URL = (typeof window !== 'undefined' && window.location && window.location.protocol !== 'file:')
    ? (window.location.origin + '/api')
    : 'http://127.0.0.1:5000/api';

function getToken() {
    return localStorage.getItem('userToken');
}

async function adminRequest(endpoint, method = 'GET', body = null) {
    const options = {
        method,
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${getToken()}` }
    };
    if (body) options.body = JSON.stringify(body);
    const res = await fetch(`${API_BASE_URL}${endpoint}`, options);
    if (res.status === 401 || res.status === 403) {
        localStorage.removeItem('userToken');
        localStorage.removeItem('userData');
        localStorage.removeItem('userName');
        localStorage.removeItem('userRole');
        const base = (typeof window !== 'undefined' && window.location.pathname && window.location.pathname.includes('/pages/')) ? '' : 'pages/';
        window.location.href = base + 'admin-login.html';
        throw new Error('Session expired');
    }
    if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.error || err.message || `Error ${res.status}`);
    }
    return res.json();
}

async function getAdminStats() {
    return adminRequest('/admin/stats');
}

async function getAdminUsers(page = 1, search = '') {
    let url = `/admin/users?page=${page}&per_page=20`;
    if (search) url += `&search=${encodeURIComponent(search)}`;
    return adminRequest(url);
}

async function getAdminUser(id) {
    return adminRequest(`/admin/users/${id}`);
}

async function deactivateUser(id) {
    return adminRequest(`/admin/users/${id}/deactivate`, 'POST');
}

async function activateUser(id) {
    return adminRequest(`/admin/users/${id}/activate`, 'POST');
}

async function deleteUser(id) {
    return adminRequest(`/admin/users/${id}/delete`, 'DELETE');
}

async function getAdminReports(page = 1, status = '') {
    let url = `/admin/reports?page=${page}&per_page=20`;
    if (status) url += `&status=${encodeURIComponent(status)}`;
    return adminRequest(url);
}

async function approveReport(id) {
    return adminRequest(`/admin/reports/${id}/approve`, 'POST');
}

async function rejectReport(id) {
    return adminRequest(`/admin/reports/${id}/reject`, 'POST');
}

async function deleteReport(id) {
    return adminRequest(`/admin/reports/${id}/delete`, 'DELETE');
}

async function getAdminAppointments(page = 1, status = '') {
    let url = `/admin/appointments?page=${page}&per_page=20`;
    if (status) url += `&status=${encodeURIComponent(status)}`;
    return adminRequest(url);
}

async function rejectAppointment(id) {
    return adminRequest(`/admin/appointments/${id}/reject`, 'POST');
}

async function getSystemHealth() {
    return adminRequest('/admin/system-health');
}

function showAdminToast(message, type = 'info') {
    if (window.healthAssistant && window.healthAssistant.showToast) {
        window.healthAssistant.showToast(message, type);
    } else {
        alert(message);
    }
}

window.adminAPI = {
    getAdminStats,
    getAdminUsers,
    getAdminUser,
    deactivateUser,
    activateUser,
    deleteUser,
    getAdminReports,
    approveReport,
    rejectReport,
    deleteReport,
    getAdminAppointments,
    rejectAppointment,
    getSystemHealth,
    showAdminToast
};
