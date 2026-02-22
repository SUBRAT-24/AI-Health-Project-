// Health Tracking JavaScript

let healthChart = null;

document.addEventListener('DOMContentLoaded', function () {
    if (!window.healthAssistant || !window.healthAssistant.isAuthenticated()) {
        window.location.href = 'login.html';
        return;
    }
    loadHealthData();
    loadHealthChart();
});

async function loadHealthData() {
    try {
        const healthData = await window.healthAssistant.getHealthData();

        if (healthData && healthData.length > 0) {
            displayRecords(healthData);
            generateSummary(healthData);
        } else {
            document.getElementById('recordsBody').innerHTML = '<tr><td colspan="6" style="text-align: center; padding: 2rem; color: #999;">No health records yet. Add data from your Dashboard.</td></tr>';
            document.getElementById('healthSummary').innerHTML = '<p style="color: #999;">No data available for summary.</p>';
        }
    } catch (error) {
        console.error('Error loading health data:', error);
    }
}

function displayRecords(records) {
    const tbody = document.getElementById('recordsBody');
    let html = '';

    records.slice(0, 50).forEach(record => {
        const date = new Date(record.timestamp);
        const dateStr = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit' });

        html += `
            <tr style="border-bottom: 1px solid #f0f0f0;">
                <td style="padding: 1rem;">${dateStr}</td>
                <td style="padding: 1rem;">${record.heart_rate || '-'} bpm</td>
                <td style="padding: 1rem;">${record.systolic || '-'}/${record.diastolic || '-'} mmHg</td>
                <td style="padding: 1rem;">${record.weight || '-'} kg</td>
                <td style="padding: 1rem;">${record.temperature || '-'} °C</td>
                <td style="padding: 1rem; font-size: 0.9rem;">${record.notes ? record.notes.substring(0, 30) + '...' : '-'}</td>
            </tr>
        `;
    });

    tbody.innerHTML = html;
}

async function loadHealthChart() {
    try {
        const days = parseInt(document.getElementById('timePeriod').value) || 30;
        const healthData = await window.healthAssistant.getHealthData(days);

        if (!healthData || healthData.length === 0) return;

        // Process data for chart
        const chartData = {
            labels: [],
            heartRate: [],
            weight: []
        };

        // Reverse to chronological order
        const sorted = [...healthData].reverse();
        sorted.forEach(record => {
            const date = new Date(record.timestamp);
            const dateStr = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
            chartData.labels.push(dateStr);
            chartData.heartRate.push(record.heart_rate || 0);
            chartData.weight.push(record.weight || 0);
        });

        renderChart(chartData);
    } catch (error) {
        console.error('Error loading chart:', error);
    }
}

function renderChart(data) {
    const ctx = document.getElementById('healthChart').getContext('2d');

    if (healthChart) {
        healthChart.destroy();
    }

    healthChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [
                {
                    label: 'Heart Rate (bpm)',
                    data: data.heartRate,
                    borderColor: '#ff6f00',
                    backgroundColor: 'rgba(255, 111, 0, 0.1)',
                    tension: 0.4
                },
                {
                    label: 'Weight (kg)',
                    data: data.weight,
                    borderColor: '#00796b',
                    backgroundColor: 'rgba(0, 121, 107, 0.1)',
                    tension: 0.4,
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    title: {
                        display: true,
                        text: 'Heart Rate (bpm)'
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    title: {
                        display: true,
                        text: 'Weight (kg)'
                    },
                    grid: {
                        drawOnChartArea: false,
                    },
                }
            }
        }
    });
}

function generateSummary(records) {
    if (!records || records.length === 0) return;

    const heartRates = records.filter(r => r.heart_rate).map(r => r.heart_rate);
    const weights = records.filter(r => r.weight).map(r => r.weight);

    let summary = '<ul style="list-style: none; padding: 0;">';

    if (heartRates.length > 0) {
        const avgHR = (heartRates.reduce((a, b) => a + b) / heartRates.length).toFixed(1);
        summary += `<li style="padding: 0.8rem; border-bottom: 1px solid #f0f0f0;">
            <strong>Average Heart Rate:</strong> ${avgHR} bpm
        </li>`;
    }

    if (weights.length > 0) {
        const avgWeight = (weights.reduce((a, b) => a + b) / weights.length).toFixed(1);
        summary += `<li style="padding: 0.8rem; border-bottom: 1px solid #f0f0f0;">
            <strong>Average Weight:</strong> ${avgWeight} kg
        </li>`;
    }

    summary += '</ul>';

    document.getElementById('healthSummary').innerHTML = summary;
}

function exportData() {
    alert('Export functionality will be implemented');
}
