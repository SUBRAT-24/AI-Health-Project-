/**
 * AI Health Assistant - Main JavaScript
 * Handles all API communication and UI interactions
 */

// ========================
// CONFIGURATION
// ========================

const API_BASE_URL = (typeof window !== 'undefined' && window.location && window.location.protocol !== 'file:')
    ? (window.location.origin + '/api')
    : 'http://127.0.0.1:5000/api';

// ========================
// UTILITY FUNCTIONS
// ========================

/**
 * Show toast notification
 */
function showToast(message, type = 'info', duration = 3000) {
    const toast = document.createElement('div');
    toast.className = `alert alert-${type}`;
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 10000;
        min-width: 300px;
        animation: slideInRight 0.3s ease-out;
    `;

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'slideInLeft 0.3s ease-out reverse';
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

/**
 * Get stored token
 */
function getToken() {
    return localStorage.getItem('userToken');
}

/**
 * Check if user is authenticated
 */
function isAuthenticated() {
    return !!localStorage.getItem('userToken');
}

// ========================
// API FUNCTIONS
// ========================

/**
 * Make API request with proper error handling
 */
async function apiRequest(endpoint, method = 'GET', body = null) {
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json',
        }
    };

    const token = getToken();
    if (token) {
        options.headers['Authorization'] = `Bearer ${token}`;
        console.log('Token sent:', token.substring(0, 20) + '...');
    } else {
        console.warn('No token found in localStorage');
    }

    if (body) {
        options.body = JSON.stringify(body);
    }

    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, options);

        if (response.status === 401 || response.status === 422) {
            // 401 = missing/unauthorized, 422 = invalid token (JWT malformed/expired)
            console.error('Auth failed:', response.status);
            localStorage.removeItem('userToken');
            localStorage.removeItem('userData');
            localStorage.removeItem('userName');
            localStorage.removeItem('userRole');
            let errMsg = 'Session invalid or expired. Please log in again.';
            try {
                const err = await response.json();
                errMsg = err.msg || err.error || err.message || errMsg;
            } catch (_) {}
            showToast(errMsg, 'error');
            const base = window.location.pathname.includes('/pages/') ? '' : 'pages/';
            const isAdmin = window.location.pathname.includes('admin');
            setTimeout(function () {
                window.location.href = base + (isAdmin ? 'admin-login.html' : 'login.html');
            }, 1500);
            return null;
        }

        if (!response.ok) {
            let errMsg = `HTTP ${response.status}`;
            try {
                const err = await response.json();
                errMsg = err.msg || err.error || err.message || errMsg;
            } catch (_) {}
            throw new Error(errMsg);
        }

        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        showToast(error.message || 'An error occurred', 'error');
        throw error;
    }
}

// ========================
// AUTHENTICATION
// ========================

async function signup(userData) {
    try {
        const response = await apiRequest('/auth/signup', 'POST', {
            name: userData.name,
            email: userData.email,
            phone: userData.phone,
            date_of_birth: userData.dob,
            gender: userData.gender,
            password: userData.password
        });

        if (response.token) {
            localStorage.setItem('userToken', response.token);
            localStorage.setItem('userName', response.name);
            localStorage.setItem('userData', JSON.stringify({
                user_id: response.user_id,
                name: response.name,
                email: userData.email
            }));
            showToast('Signup successful! Redirecting...', 'success');
            setTimeout(() => {
                window.location.href = 'dashboard.html';
            }, 1500);
        }
    } catch (error) {
        showToast('Signup failed: ' + error.message, 'error');
    }
}

async function login(email, password) {
    try {
        const response = await apiRequest('/auth/login', 'POST', {
            email,
            password
        });

        if (response.token) {
            localStorage.setItem('userToken', response.token);
            localStorage.setItem('userName', response.name);
            const role = response.role || 'user';
            localStorage.setItem('userRole', role);
            localStorage.setItem('userData', JSON.stringify({
                user_id: response.user_id,
                name: response.name,
                email: response.email,
                role
            }));
            showToast('Login successful!', 'success');
            const redirect = role === 'admin' ? 'admin-dashboard.html' : 'dashboard.html';
            setTimeout(() => {
                window.location.href = redirect;
            }, 1000);
        }
    } catch (error) {
        showToast('Login failed: ' + error.message, 'error');
    }
}

function logout() {
    localStorage.removeItem('userToken');
    localStorage.removeItem('userData');
    localStorage.removeItem('userName');
    localStorage.removeItem('userRole');
    showToast('Logged out successfully', 'info');
    setTimeout(() => {
        window.location.href = '../index.html';
    }, 1000);
}

// Alias for pages that call logoutUser
function logoutUser() {
    logout();
}

// ========================
// HEALTH TRACKING
// ========================

async function updateHealthMetrics(metrics) {
    try {
        await apiRequest('/health/update', 'POST', {
            heart_rate: parseInt(metrics.heart_rate) || 0,
            systolic: parseInt(metrics.systolic) || 0,
            diastolic: parseInt(metrics.diastolic) || 0,
            weight: parseFloat(metrics.weight) || 0,
            temperature: parseFloat(metrics.temperature) || 37,
            blood_glucose: parseFloat(metrics.blood_glucose) || null,
            oxygen_saturation: parseFloat(metrics.oxygen_saturation) || null,
            notes: metrics.notes || ''
        });

        showToast('Health data updated successfully!', 'success');
    } catch (error) {
        showToast('Failed to update health data', 'error');
    }
}

async function getHealthData(days = 30) {
    try {
        const response = await apiRequest(`/health/data?days=${days}`);
        return response.records || [];
    } catch (error) {
        return [];
    }
}

async function getHealthSummary() {
    try {
        return await apiRequest('/health/summary');
    } catch (error) {
        return null;
    }
}

// ========================
// APPOINTMENTS
// ========================

async function bookAppointment(data) {
    try {
        await apiRequest('/appointments/book', 'POST', {
            doctor_name: data.doctor,
            doctor_specialization: data.specialization,
            appointment_date: data.appointment_date || data.date,
            reason: data.reason
        });

        showToast('Appointment booked!', 'success');
    } catch (error) {
        showToast('Failed to book appointment', 'error');
    }
}

async function getAppointments() {
    try {
        const response = await apiRequest('/appointments/list');
        return response.appointments || response || [];
    } catch (error) {
        return [];
    }
}

async function cancelAppointment(id) {
    try {
        await apiRequest(`/appointments/${id}/cancel`, 'DELETE');
        showToast('Appointment cancelled', 'success');
    } catch (error) {
        showToast('Failed to cancel appointment', 'error');
    }
}

// ========================
// MEDICAL REPORTS
// ========================

async function uploadReport(file, description) {
    try {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('description', description || '');

        const token = getToken();
        const response = await fetch(`${API_BASE_URL}/reports/upload`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: formData
        });

        if (!response.ok) {
            let errMsg = 'Upload failed';
            try {
                const err = await response.json();
                errMsg = err.error || err.message || errMsg;
            } catch (_) {}
            throw new Error(errMsg);
        }

        showToast('Report uploaded!', 'success');
    } catch (error) {
        showToast('Upload failed: ' + error.message, 'error');
    }
}

async function getReports() {
    try {
        const response = await apiRequest('/reports/list');
        return response.reports || [];
    } catch (error) {
        return [];
    }
}

// ========================
// RECOMMENDATIONS
// ========================

async function getDietRecommendations(age, gender, condition) {
    try {
        return await apiRequest('/diet/recommendations', 'POST', {
            age: parseInt(age),
            gender,
            health_condition: condition
        });
    } catch (error) {
        return null;
    }
}

async function getExerciseRecommendations(level) {
    try {
        return await apiRequest('/exercise/recommendations', 'POST', {
            fitness_level: level
        });
    } catch (error) {
        return null;
    }
}

// ========================
// CHATBOT
// ========================

async function sendChatMessage(message) {
    try {
        const response = await apiRequest('/chatbot/message', 'POST', {
            message
        });
        return response.response || response.message || 'No response';
    } catch (error) {
        return 'Sorry, I could not process that.';
    }
}

// ========================
// INITIALIZATION
// ========================

document.addEventListener('DOMContentLoaded', function () {
    console.log('✓ AI Health Assistant loaded');

    // Test API connectivity
    testAPIConnectivity();
});

/**
 * Test API connectivity
 */
async function testAPIConnectivity() {
    try {
        const base = (typeof window !== 'undefined' && window.location && window.location.protocol !== 'file:')
            ? (window.location.origin + '/api') : 'http://127.0.0.1:5000/api';
        const response = await fetch(base + '/health/test');
        const data = await response.json();
        console.log('✓ API Test Result:', data);

        // Now test with auth endpoint
        const token = getToken();
        if (token) {
            console.log('✓ Token found:', token.substring(0, 20) + '...');
        } else {
            console.warn('⚠ No token in localStorage');
        }
    } catch (error) {
        console.error('✗ API Test Failed:', error);
    }
}

// Export all functions
window.healthAssistant = {
    signup,
    login,
    logout,
    logoutUser,
    updateHealthMetrics,
    getHealthData,
    getHealthSummary,
    bookAppointment,
    getAppointments,
    cancelAppointment,
    uploadReport,
    getReports,
    getDietRecommendations,
    getExerciseRecommendations,
    sendChatMessage,
    apiRequest,
    showToast,
    isAuthenticated,
};

