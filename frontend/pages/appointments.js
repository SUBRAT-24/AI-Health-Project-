// Appointments JavaScript

document.addEventListener('DOMContentLoaded', function () {
    if (!window.healthAssistant || !window.healthAssistant.isAuthenticated()) {
        window.location.href = 'login.html';
        return;
    }
    loadAppointments();
    setupFormListener();
});

function setupFormListener() {
    const form = document.getElementById('appointmentForm');
    if (form) {
        form.addEventListener('submit', handleBookAppointment);
    }
}

async function loadAppointments() {
    try {
        const appointments = await window.healthAssistant.getAppointments();
        const tbody = document.getElementById('appointmentsBody');

        if (appointments && appointments.length > 0) {
            let html = '';
            appointments.forEach(apt => {
                const spec = apt.doctor_specialization || apt.specialization || 'N/A';
                const dateStr = apt.appointment_date
                    ? new Date(apt.appointment_date).toLocaleString('en-US', { dateStyle: 'medium', timeStyle: 'short' })
                    : 'N/A';

                html += `
                    <tr style="border-bottom: 1px solid #f0f0f0;">
                        <td style="padding: 1rem;">Dr. ${apt.doctor_name || 'N/A'}</td>
                        <td style="padding: 1rem;">${spec}</td>
                        <td style="padding: 1rem;">${dateStr}</td>
                        <td style="padding: 1rem;">
                            <span style="color: ${apt.status === 'confirmed' ? '#4caf50' : apt.status === 'cancelled' ? '#f44336' : '#ff9800'};
                                         font-weight: 600; padding: 0.3rem 0.8rem;
                                         background: ${apt.status === 'confirmed' ? '#e8f5e9' : apt.status === 'cancelled' ? '#ffebee' : '#fff3e0'};
                                         border-radius: 4px;">
                                    ${apt.status}
                            </span>
                        </td>
                        <td style="padding: 1rem;">
                            ${apt.status !== 'cancelled' ? `<button class="btn btn-secondary" style="padding: 0.4rem 0.8rem; font-size: 0.85rem; background: #f44336; color: white;" onclick="confirmCancel(${apt.id})">Cancel</button>` : ''}
                        </td>
                    </tr>
                `;
            });
            tbody.innerHTML = html;
        } else {
            tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; padding: 2rem; color: #999;">No appointments scheduled</td></tr>';
        }
    } catch (error) {
        console.error('Error loading appointments:', error);
    }
}

async function handleBookAppointment(e) {
    e.preventDefault();

    const dateTimeValue = document.getElementById('appointmentDate').value;
    // datetime-local gives "YYYY-MM-DDTHH:mm" - append :00 if needed for ISO
    const appointmentDate = dateTimeValue.length === 16 ? dateTimeValue + ':00' : dateTimeValue;

    const appointmentData = {
        doctor: document.getElementById('doctorName').value,
        specialization: document.getElementById('specialization').value,
        appointment_date: appointmentDate,
        reason: document.getElementById('reason').value
    };

    try {
        await window.healthAssistant.bookAppointment(appointmentData);
        closeBookModal();
        document.getElementById('appointmentForm').reset();
        loadAppointments();
    } catch (error) {
        console.error('Error booking appointment:', error);
    }
}

function openBookModal() {
    document.getElementById('bookModal').style.display = 'block';
}

function closeBookModal() {
    document.getElementById('bookModal').style.display = 'none';
}

async function confirmCancel(appointmentId) {
    if (confirm('Are you sure you want to cancel this appointment?')) {
        try {
            await window.healthAssistant.cancelAppointment(appointmentId);
            loadAppointments();
        } catch (error) {
            console.error('Error cancelling appointment:', error);
        }
    }
}

window.onclick = function (event) {
    const modal = document.getElementById('bookModal');
    if (event.target == modal) {
        modal.style.display = 'none';
    }
}
