/**
 * Dashboard JavaScript
 * Connects the new dashboard UI with the Flask backend API
 */

document.addEventListener('DOMContentLoaded', function () {
    if (!window.healthAssistant.isAuthenticated()) {
        window.location.href = 'login.html';
        return;
    }
    loadDashboardData();
    setupDashboardListeners();
});

// ========================
// SETUP
// ========================

function setupDashboardListeners() {
    const healthForm = document.getElementById('healthForm');
    if (healthForm) {
        healthForm.addEventListener('submit', handleHealthFormSubmit);
    }

    // Refresh insights button
    const refreshBtn = document.getElementById('refreshInsights');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', loadHealthInsights);
    }

    // Export button
    const exportBtn = document.getElementById('exportBtn');
    if (exportBtn) {
        exportBtn.addEventListener('click', exportHealthReport);
    }
}

// ========================
// MAIN DATA LOADER
// ========================

async function loadDashboardData() {
    // Load user name into topbar + page
    const userName = localStorage.getItem('userName') || 'User';
    const userData = JSON.parse(localStorage.getItem('userData') || '{}');

    // Topbar info
    const topbarNameEl = document.getElementById('topbarUserName');
    const topbarEmailEl = document.getElementById('topbarUserEmail');
    const avatarEl = document.getElementById('userAvatar');
    const userNameEl = document.getElementById('userName');

    if (topbarNameEl) topbarNameEl.textContent = userName;
    if (topbarEmailEl) topbarEmailEl.textContent = userData.email || 'user@health.com';
    if (avatarEl) avatarEl.textContent = userName.charAt(0).toUpperCase();
    if (userNameEl) userNameEl.textContent = userName;

    // Load all data concurrently
    await Promise.allSettled([
        loadHealthStats(),
        loadHealthInsights(),
        loadRecentActivity(),
        loadHealthChart(),
        loadAppointmentBadge(),
        loadReminders()
    ]);
}

// ========================
// STAT CARDS
// ========================

async function loadHealthStats() {
    try {
        const healthData = await window.healthAssistant.getHealthData(30);
        if (healthData && healthData.length > 0) {
            const latest = healthData[0];
            updateStatCards(latest);
            updateRecentReadings(latest);
        } else {
            // No data yet — show placeholder
            setStatCardEmpty();
        }
    } catch (error) {
        console.error('Error loading health stats:', error);
        setStatCardEmpty();
    }
}

function updateStatCards(data) {
    if (!data) return;

    // Heart Rate
    if (data.heart_rate) {
        const hrEl = document.getElementById('heartRate');
        if (hrEl) {
            hrEl.textContent = data.heart_rate;
            animateValue(hrEl, 0, data.heart_rate, 800);
        }

        const hrChange = document.getElementById('heartRateChange');
        if (hrChange) {
            if (data.heart_rate < 60) {
                hrChange.innerHTML = '⚠️ Below normal';
                hrChange.classList.add('negative');
            } else if (data.heart_rate > 100) {
                hrChange.innerHTML = '⚠️ Elevated';
                hrChange.classList.add('negative');
            } else {
                hrChange.innerHTML = '✅ Normal range';
            }
        }
    }

    // Blood Pressure
    if (data.systolic && data.diastolic) {
        const bpEl = document.getElementById('bloodPressure');
        if (bpEl) bpEl.textContent = `${data.systolic}/${data.diastolic}`;

        const bpChange = document.getElementById('bpChange');
        if (bpChange) {
            if (data.systolic >= 140 || data.diastolic >= 90) {
                bpChange.innerHTML = '⚠️ High – consult doctor';
                bpChange.classList.add('negative');
            } else if (data.systolic >= 130 || data.diastolic >= 80) {
                bpChange.innerHTML = '⚠️ Slightly elevated';
                bpChange.classList.add('negative');
            } else {
                bpChange.innerHTML = '✅ Normal range';
            }
        }
    }

    // Weight
    if (data.weight) {
        const wEl = document.getElementById('weight');
        if (wEl) wEl.textContent = `${data.weight} kg`;

        const wChange = document.getElementById('weightChange');
        if (wChange) wChange.innerHTML = `📊 Last recorded`;
    }

    // BMI
    if (data.weight) {
        const height = 1.75; // Default — should come from user profile
        const bmi = (data.weight / (height * height)).toFixed(1);
        const bmiEl = document.getElementById('bmi');
        if (bmiEl) bmiEl.textContent = bmi;

        const bmiStatus = document.getElementById('bmiStatus');
        if (bmiStatus) {
            const bmiVal = parseFloat(bmi);
            if (bmiVal < 18.5) bmiStatus.textContent = 'Underweight';
            else if (bmiVal < 25) bmiStatus.textContent = 'Normal weight';
            else if (bmiVal < 30) bmiStatus.textContent = 'Overweight';
            else bmiStatus.textContent = 'Obese';
        }
    }

    // Update date labels in recent readings
    const timestamp = data.timestamp ? formatTime(data.timestamp) : 'Just now';
    ['hrDate', 'bpDate', 'weightDate', 'tempDate'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.textContent = timestamp;
    });

    // Update status badges in recent readings
    updateReadingStatus('hrStatus', data.heart_rate, 60, 100, 'Normal', 'Low', 'High');
    updateBPStatus(data.systolic, data.diastolic);
    updateReadingStatus('tempStatus', data.temperature, 36.0, 37.5, 'Normal', 'Low', 'Fever');
}

function updateReadingStatus(elId, value, low, high, normalText, lowText, highText) {
    const el = document.getElementById(elId);
    if (!el || !value) return;

    el.classList.remove('normal', 'warning', 'critical');
    if (value < low) {
        el.textContent = lowText;
        el.classList.add('warning');
    } else if (value > high) {
        el.textContent = highText;
        el.classList.add('critical');
    } else {
        el.textContent = normalText;
        el.classList.add('normal');
    }
}

function updateBPStatus(systolic, diastolic) {
    const el = document.getElementById('bpStatus');
    if (!el) return;

    el.classList.remove('normal', 'warning', 'critical');
    if (!systolic || !diastolic) return;

    if (systolic >= 140 || diastolic >= 90) {
        el.textContent = 'High';
        el.classList.add('critical');
    } else if (systolic >= 130 || diastolic >= 80) {
        el.textContent = 'Elevated';
        el.classList.add('warning');
    } else {
        el.textContent = 'Normal';
        el.classList.add('normal');
    }
}

function updateRecentReadings(data) {
    const exerciseDateEl = document.getElementById('exerciseDate');
    if (exerciseDateEl) {
        exerciseDateEl.textContent = data.timestamp ? formatTime(data.timestamp) : '--';
    }
}

function setStatCardEmpty() {
    const ids = ['heartRate', 'bloodPressure', 'weight', 'bmi'];
    const defaults = ['--', '--/--', '-- kg', '--'];

    ids.forEach((id, i) => {
        const el = document.getElementById(id);
        if (el) el.textContent = defaults[i];
    });
}

// ========================
// HEALTH CHART (Weekly Analytics)
// ========================

async function loadHealthChart() {
    try {
        const healthData = await window.healthAssistant.getHealthData(7);
        if (!healthData || healthData.length === 0) return;

        const chartContainer = document.getElementById('healthChart');
        if (!chartContainer) return;

        // Group data by day of week
        const dayLabels = ['M', 'T', 'W', 'T', 'F', 'S', 'S'];
        const dayData = new Array(7).fill(0);
        const dayCounts = new Array(7).fill(0);

        healthData.forEach(record => {
            if (record.heart_rate) {
                const date = new Date(record.timestamp);
                const dayIndex = (date.getDay() + 6) % 7; // Mon=0
                dayData[dayIndex] += record.heart_rate;
                dayCounts[dayIndex]++;
            }
        });

        // Build chart bars from real data
        const maxVal = Math.max(...dayData.map((v, i) => dayCounts[i] ? v / dayCounts[i] : 0), 1);

        let chartHTML = '';
        dayLabels.forEach((label, i) => {
            const avg = dayCounts[i] > 0 ? Math.round(dayData[i] / dayCounts[i]) : 0;
            const heightPercent = maxVal > 0 && avg > 0 ? Math.max((avg / (maxVal * 1.2)) * 100, 10) : 15;

            chartHTML += `
                <div class="chart-bar-group">
                    <div class="chart-bar" style="height: ${heightPercent}%;" data-value="${avg}">
                        <span class="chart-bar-value">${avg || '--'}</span>
                    </div>
                    <span class="chart-bar-label">${label}</span>
                </div>
            `;
        });

        chartContainer.innerHTML = chartHTML;

    } catch (error) {
        console.error('Error loading health chart:', error);
    }
}

// ========================
// HEALTH INSIGHTS (AI Analysis)
// ========================

async function loadHealthInsights() {
    const insightsContainer = document.getElementById('healthInsights');
    if (!insightsContainer) return;

    try {
        const healthData = await window.healthAssistant.getHealthData(30);

        if (!healthData || healthData.length === 0) {
            insightsContainer.innerHTML = `
                <div class="team-member">
                    <div class="team-avatar c">💡</div>
                    <div class="team-info">
                        <div class="team-name">No data yet</div>
                        <div class="team-task">Add health data to get <strong>AI insights</strong></div>
                    </div>
                </div>
            `;
            return;
        }

        const latest = healthData[0];
        let insights = [];

        // Generate insights from real data
        // Heart Rate
        if (latest.heart_rate) {
            if (latest.heart_rate < 60) {
                insights.push({ icon: '💓', name: 'Heart Rate Low', task: 'Your heart rate is <strong>below 60 bpm</strong> — consult a doctor', status: 'pending', statusLabel: 'Attention' });
            } else if (latest.heart_rate > 100) {
                insights.push({ icon: '💓', name: 'Heart Rate Elevated', task: 'Try <strong>relaxation techniques</strong> to lower heart rate', status: 'pending', statusLabel: 'Attention' });
            } else {
                insights.push({ icon: '💓', name: 'Heart Rate Normal', task: 'Your heart rate is <strong>' + latest.heart_rate + ' bpm</strong> — keep it up!', status: 'completed', statusLabel: '✓' });
            }
        }

        // Blood Pressure
        if (latest.systolic && latest.diastolic) {
            if (latest.systolic >= 140 || latest.diastolic >= 90) {
                insights.push({ icon: '🩺', name: 'Blood Pressure High', task: 'BP is <strong>' + latest.systolic + '/' + latest.diastolic + '</strong> — consult doctor', status: 'pending', statusLabel: 'Critical' });
            } else if (latest.systolic < 120 && latest.diastolic < 80) {
                insights.push({ icon: '🩺', name: 'Blood Pressure Normal', task: 'BP is <strong>' + latest.systolic + '/' + latest.diastolic + '</strong> — excellent!', status: 'completed', statusLabel: '✓' });
            } else {
                insights.push({ icon: '🩺', name: 'Blood Pressure Elevated', task: 'BP is <strong>' + latest.systolic + '/' + latest.diastolic + '</strong> — monitor regularly', status: 'progress', statusLabel: 'Monitor' });
            }
        }

        // Temperature
        if (latest.temperature) {
            if (latest.temperature > 37.5) {
                insights.push({ icon: '🌡️', name: 'Fever Detected', task: 'Temperature is <strong>' + latest.temperature + '°C</strong> — rest and hydrate', status: 'pending', statusLabel: 'Attention' });
            } else {
                insights.push({ icon: '🌡️', name: 'Temperature Normal', task: 'Body temp is <strong>' + latest.temperature + '°C</strong> — all good', status: 'completed', statusLabel: '✓' });
            }
        }

        // General recommendations
        insights.push({ icon: '💧', name: 'Stay Hydrated', task: 'Drink at least <strong>8 glasses</strong> of water daily', status: 'progress', statusLabel: 'Ongoing' });
        insights.push({ icon: '😴', name: 'Quality Sleep', task: 'Aim for <strong>7-9 hours</strong> of sleep every night', status: 'progress', statusLabel: 'Ongoing' });

        // Render
        const avatarClasses = ['a', 'b', 'c', 'd', 'a', 'b'];
        insightsContainer.innerHTML = insights.map((item, idx) => `
            <div class="team-member">
                <div class="team-avatar ${avatarClasses[idx % avatarClasses.length]}">${item.icon}</div>
                <div class="team-info">
                    <div class="team-name">${item.name}</div>
                    <div class="team-task">${item.task}</div>
                </div>
                <span class="team-status ${item.status}">${item.statusLabel}</span>
            </div>
        `).join('');

        // Update wellness progress circle
        updateWellnessScore(latest);

    } catch (error) {
        console.error('Error loading health insights:', error);
    }
}

function updateWellnessScore(latestData) {
    let score = 50; // Base score
    let checks = 0;
    let goodChecks = 0;

    if (latestData.heart_rate) {
        checks++;
        if (latestData.heart_rate >= 60 && latestData.heart_rate <= 100) goodChecks++;
    }
    if (latestData.systolic && latestData.diastolic) {
        checks++;
        if (latestData.systolic < 130 && latestData.diastolic < 85) goodChecks++;
    }
    if (latestData.temperature) {
        checks++;
        if (latestData.temperature <= 37.5 && latestData.temperature >= 36.0) goodChecks++;
    }
    if (latestData.weight) {
        checks++;
        const bmi = latestData.weight / (1.75 * 1.75);
        if (bmi >= 18.5 && bmi <= 25) goodChecks++;
    }

    if (checks > 0) {
        score = Math.round((goodChecks / checks) * 100);
    }

    const progressValueEl = document.getElementById('progressValue');
    if (progressValueEl) {
        progressValueEl.textContent = score + '%';
    }

    // Update SVG circle
    const progressFill = document.getElementById('progressFill');
    if (progressFill) {
        const circumference = 2 * Math.PI * 70; // r = 70
        const offset = circumference - (score / 100) * circumference;
        progressFill.style.strokeDasharray = circumference;
        progressFill.style.strokeDashoffset = offset;
    }
}

// ========================
// RECENT ACTIVITY (Appointments)
// ========================

async function loadRecentActivity() {
    try {
        const appointments = await window.healthAssistant.getAppointments();
        const activityDiv = document.getElementById('recentActivity');

        if (!activityDiv) return;

        if (!appointments || appointments.length === 0) {
            activityDiv.innerHTML = `
                <tr>
                    <td colspan="3" style="text-align: center; padding: 2rem; color: var(--text-muted);">
                        No appointments yet. <a href="appointments.html" style="color: var(--primary-green); font-weight: 600;">Book one now →</a>
                    </td>
                </tr>
            `;
            return;
        }

        let html = '';
        appointments.slice(0, 5).forEach(apt => {
            const statusColor = {
                'scheduled': 'progress',
                'confirmed': 'completed',
                'completed': 'completed',
                'cancelled': 'pending'
            };
            const statusClass = statusColor[apt.status] || 'progress';

            html += `
                <tr>
                    <td>${formatDate(apt.appointment_date)}</td>
                    <td>🩺 Appointment with Dr. ${apt.doctor_name}</td>
                    <td>
                        <span class="health-item-status ${statusClass === 'completed' ? 'normal' : statusClass === 'pending' ? 'critical' : 'warning'}">
                            ${apt.status}
                        </span>
                    </td>
                </tr>
            `;
        });
        activityDiv.innerHTML = html;

    } catch (error) {
        console.error('Error loading activity:', error);
    }
}

// ========================
// APPOINTMENT BADGE
// ========================

async function loadAppointmentBadge() {
    try {
        const appointments = await window.healthAssistant.getAppointments();
        const badge = document.getElementById('appointmentBadge');

        if (!badge || !appointments) return;

        const upcoming = appointments.filter(a =>
            a.status !== 'cancelled' &&
            a.status !== 'completed' &&
            new Date(a.appointment_date) >= new Date()
        );

        if (upcoming.length > 0) {
            badge.textContent = upcoming.length;
            badge.style.display = 'inline';
        } else {
            badge.style.display = 'none';
        }
    } catch (error) {
        console.error('Error loading badge:', error);
    }
}

// ========================
// REMINDERS
// ========================

async function loadReminders() {
    const container = document.getElementById('remindersContainer');
    if (!container) return;

    try {
        const appointments = await window.healthAssistant.getAppointments();

        // Find next upcoming appointment
        const upcoming = (appointments || [])
            .filter(a => a.status !== 'cancelled' && new Date(a.appointment_date) >= new Date())
            .sort((a, b) => new Date(a.appointment_date) - new Date(b.appointment_date));

        let html = '';

        if (upcoming.length > 0) {
            const next = upcoming[0];
            const aptDate = new Date(next.appointment_date);
            html += `
                <div class="reminder-item">
                    <div class="reminder-label">Upcoming</div>
                    <div class="reminder-title">Dr. ${next.doctor_name} — ${next.doctor_specialization || 'General'}</div>
                    <div class="reminder-time">⏰ ${aptDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })} at ${aptDate.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}</div>
                    <button class="btn-reminder" onclick="window.location.href='appointments.html'">View Appointment</button>
                </div>
            `;
        } else {
            html += `
                <div class="reminder-item">
                    <div class="reminder-label">No Upcoming</div>
                    <div class="reminder-title">No appointments scheduled</div>
                    <div class="reminder-time">📅 Book your next appointment</div>
                    <button class="btn-reminder" onclick="window.location.href='appointments.html'">Book Now</button>
                </div>
            `;
        }

        // Always show medication reminder
        html += `
            <div class="reminder-item">
                <div class="reminder-label">Daily</div>
                <div class="reminder-title">Health Check-in</div>
                <div class="reminder-time">💊 Log your daily vitals for better AI insights</div>
            </div>
        `;

        container.innerHTML = html;

    } catch (error) {
        console.error('Error loading reminders:', error);
    }
}

// ========================
// HEALTH FORM SUBMIT
// ========================

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
        document.getElementById('healthForm').reset();

        // Reload all dashboard data
        await loadDashboardData();

        window.healthAssistant.showToast('Health data saved successfully!', 'success');
    } catch (error) {
        console.error('Error updating health metrics:', error);
    }
}

// ========================
// MODAL
// ========================

function openHealthModal() {
    const modal = document.getElementById('healthModal');
    if (modal) {
        modal.style.display = 'flex';
        modal.classList.add('active');
    }
}

function closeHealthModal() {
    const modal = document.getElementById('healthModal');
    if (modal) {
        modal.style.display = 'none';
        modal.classList.remove('active');
    }
}

// Close modal on background click
window.addEventListener('click', function (event) {
    const modal = document.getElementById('healthModal');
    if (event.target === modal) {
        closeHealthModal();
    }
});

// ========================
// EXPORT
// ========================

async function exportHealthReport() {
    try {
        const healthData = await window.healthAssistant.getHealthData(30);
        if (!healthData || healthData.length === 0) {
            window.healthAssistant.showToast('No health data to export', 'info');
            return;
        }

        // Build CSV
        const headers = ['Date', 'Heart Rate', 'Systolic', 'Diastolic', 'Weight', 'Temperature', 'Notes'];
        let csv = headers.join(',') + '\n';

        healthData.forEach(record => {
            csv += [
                record.timestamp,
                record.heart_rate || '',
                record.systolic || '',
                record.diastolic || '',
                record.weight || '',
                record.temperature || '',
                (record.notes || '').replace(/,/g, ';')
            ].join(',') + '\n';
        });

        // Download
        const blob = new Blob([csv], { type: 'text/csv' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `health_report_${new Date().toISOString().split('T')[0]}.csv`;
        a.click();
        URL.revokeObjectURL(url);

        window.healthAssistant.showToast('Report exported successfully!', 'success');
    } catch (error) {
        console.error('Error exporting report:', error);
        window.healthAssistant.showToast('Failed to export report', 'error');
    }
}

// ========================
// UTILITIES
// ========================

function formatDate(dateStr) {
    return new Date(dateStr).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
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

function animateValue(element, start, end, duration) {
    const startTime = performance.now();
    const endVal = parseInt(end);
    const startVal = parseInt(start);

    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 3); // ease-out cubic
        const current = Math.round(startVal + (endVal - startVal) * eased);
        element.textContent = current;

        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }

    requestAnimationFrame(update);
}
