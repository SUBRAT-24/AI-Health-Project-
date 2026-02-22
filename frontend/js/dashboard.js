// Dashboard JavaScript

document.addEventListener('DOMContentLoaded', function() {
    if (!window.healthAssistant.isAuthenticated()) {
        window.location.href = 'login.html';
        return;
    }
    loadDashboardData();
    setupDashboardListeners();
});

function setupDashboardListeners() {
    const healthForm = document.getElementById('healthForm');
    if (healthForm) {
        healthForm.addEventListener('submit', handleHealthFormSubmit);
    }
}

async function loadDashboardData() {
    // Load user name
    const userName = localStorage.getItem('userName');
    document.getElementById('userName').textContent = userName || 'User';

    // Load health data
    try {
        const healthData = await window.healthAssistant.getHealthData();
        if (healthData && healthData.length > 0) {
            const latestData = healthData[0];
            updateHealthStatus(latestData);
        }
    } catch (error) {
        console.error('Error loading health data:', error);
    }

    // Load health insights
    loadHealthInsights();

    // Load recent activity
    loadRecentActivity();
}

function updateHealthStatus(data) {
    if (!data) return;
    
    if (data.heart_rate) {
        document.getElementById('heartRate').textContent = data.heart_rate + ' bpm';
        document.getElementById('heartRateTime').textContent = formatTime(data.timestamp);
    }

    if (data.systolic && data.diastolic) {
        document.getElementById('bloodPressure').textContent = 
            data.systolic + '/' + data.diastolic + ' mmHg';
        document.getElementById('bpTime').textContent = formatTime(data.timestamp);
    }

    if (data.weight) {
        document.getElementById('weight').textContent = data.weight + ' kg';
        document.getElementById('weightTime').textContent = formatTime(data.timestamp);
        
        // Calculate BMI
        const height = 1.75; // Placeholder - should come from user profile
        const bmi = (data.weight / (height * height)).toFixed(1);
        document.getElementById('bmi').textContent = bmi;
    }
}

async function loadHealthInsights() {
    try {
        const insights = await window.healthAssistant.getHealthData();
        const insightsDiv = document.getElementById('healthInsights');
        
        if (!insights || insights.length === 0) {
            insightsDiv.innerHTML = '<p style="color: #999;">No health data yet. Add health data to get insights.</p>';
            return;
        }
        
        if (insights && insights.length > 0) {
            const latestData = insights[0];
            
            let insightText = '<h3>Current Health Status</h3>';
            insightText += '<ul style="list-style: none; padding: 0;">';
            
            // Heart Rate Analysis
            if (latestData.heart_rate < 60) {
                insightText += '<li>💓 Heart Rate: <strong style="color: #ff6f00;">Lower than normal</strong> - Consider consulting a doctor</li>';
            } else if (latestData.heart_rate > 100) {
                insightText += '<li>💓 Heart Rate: <strong style="color: #ff6f00;">Elevated</strong> - Try relaxation techniques</li>';
            } else {
                insightText += '<li>💓 Heart Rate: <strong style="color: #4caf50;">Normal</strong> - Keep it up!</li>';
            }

            // Blood Pressure Analysis
            if (latestData.systolic < 120 && latestData.diastolic < 80) {
                insightText += '<li>🧊 Blood Pressure: <strong style="color: #4caf50;">Normal</strong> - Good health status</li>';
            } else if (latestData.systolic >= 130 || latestData.diastolic >= 80) {
                insightText += '<li>🧊 Blood Pressure: <strong style="color: #ff6f00;">Elevated</strong> - Monitor regularly</li>';
            } else {
                insightText += '<li>🧊 Blood Pressure: <strong style="color: #ff9800;">Slightly high</strong> - Reduce stress</li>';
            }

            insightText += '</ul>';
            
            // AI Recommendations
            insightText += '<h3 style="margin-top: 1.5rem;">AI Recommendations</h3>';
            insightText += '<ul style="list-style: none; padding: 0;">';
            insightText += '<li>✓ Stay hydrated - drink at least 8 glasses of water daily</li>';
            insightText += '<li>✓ Exercise for 30 minutes daily for optimal health</li>';
            insightText += '<li>✓ Maintain a balanced diet with vegetables and proteins</li>';
            insightText += '<li>✓ Get 7-9 hours of quality sleep every night</li>';
            insightText += '</ul>';

            insightsDiv.innerHTML = insightText;
        }
    } catch (error) {
        console.error('Error loading insights:', error);
    }
}

async function loadRecentActivity() {
    try {
        const appointments = await window.healthAssistant.getAppointments();
        const activityDiv = document.getElementById('recentActivity');
        
        if (!appointments || appointments.length === 0) {
            activityDiv.innerHTML = '<p style="color: #999;">No appointments scheduled. <a href="appointments.html" style="color: #00796b; font-weight: bold;">Book one now</a></p>';
            return;
        }
        
        if (appointments && appointments.length > 0) {
            let html = '';
            appointments.slice(0, 5).forEach(apt => {
                html += `<tr style="border-bottom: 1px solid #f0f0f0;">
                    <td style="padding: 1rem;">${formatDate(apt.appointment_date)}</td>
                    <td style="padding: 1rem;">Appointment with Dr. ${apt.doctor_name}</td>
                    <td style="padding: 1rem;">
                        <span style="color: ${apt.status === 'confirmed' ? '#4caf50' : '#ff9800'};
                                     font-weight: 600;">${apt.status}</span>
                    </td>
                </tr>`;
            });
            activityDiv.innerHTML = html;
        }
    } catch (error) {
        console.error('Error loading activity:', error);
    }
}

async function handleHealthFormSubmit(e) {
    e.preventDefault();

    const healthData = {
        heart_rate: parseInt(document.getElementById('heartRateInput').value),
        systolic: parseInt(document.getElementById('systolic').value),
        diastolic: parseInt(document.getElementById('diastolic').value),
        weight: parseFloat(document.getElementById('weightInput').value),
        temperature: parseFloat(document.getElementById('temperature').value),
        notes: document.getElementById('notes').value
    };

    try {
        await window.healthAssistant.updateHealthMetrics(healthData);
        closeHealthModal();
        loadDashboardData();
        document.getElementById('healthForm').reset();
    } catch (error) {
        console.error('Error updating health metrics:', error);
    }
}

function openHealthModal() {
    document.getElementById('healthModal').style.display = 'block';
}

function closeHealthModal() {
    document.getElementById('healthModal').style.display = 'none';
}

function formatDate(dateStr) {
    return new Date(dateStr).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric'
    });
}

function formatTime(dateStr) {
    return new Date(dateStr).toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Window close listener to prevent closing when pressing escape
window.onclick = function(event) {
    const modal = document.getElementById('healthModal');
    if (event.target == modal) {
        modal.style.display = 'none';
    }
}
