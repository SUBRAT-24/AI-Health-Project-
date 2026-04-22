// Appointments JavaScript - Connected to Flask Backend

document.addEventListener('DOMContentLoaded', function () {
    if (!window.healthAssistant.isAuthenticated()) {
        window.location.href = 'login.html';
        return;
    }
    loadAppointments();
    setupForm();
});

function setupForm() {
    const form = document.getElementById('appointmentForm');
    if (form) {
        form.addEventListener('submit', handleBookAppointment);
    }
}

async function loadAppointments() {
    const tbody = document.getElementById('appointmentsBody');
    if (!tbody) return;

    try {
        const appointments = await window.healthAssistant.getAppointments();

        if (!appointments || appointments.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="5" style="text-align: center; padding: 3rem; color: var(--text-muted);">
                        No appointments yet. Click "Book Appointment" to schedule one.
                    </td>
                </tr>
            `;
            return;
        }

        tbody.innerHTML = appointments.map(apt => {
            const statusMap = {
                'scheduled': { cls: 'warning', label: 'Scheduled' },
                'confirmed': { cls: 'normal', label: 'Confirmed' },
                'completed': { cls: 'normal', label: 'Completed' },
                'cancelled': { cls: 'critical', label: 'Cancelled' }
            };
            const status = statusMap[apt.status] || statusMap['scheduled'];
            const aptDate = new Date(apt.appointment_date);

            return `
                <tr>
                    <td>🩺 Dr. ${apt.doctor_name}</td>
                    <td>${apt.doctor_specialization || 'General'}</td>
                    <td>${aptDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })} at ${aptDate.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}</td>
                    <td><span class="health-item-status ${status.cls}">${status.label}</span></td>
                    <td>
                        ${apt.status !== 'cancelled' && apt.status !== 'completed' ? `
                            <button class="btn btn-sm btn-danger" onclick="cancelAppointment(${apt.id})">Cancel</button>
                        ` : '--'}
                    </td>
                </tr>
            `;
        }).join('');

    } catch (error) {
        console.error('Error loading appointments:', error);
        tbody.innerHTML = `
            <tr>
                <td colspan="5" style="text-align: center; padding: 2rem; color: var(--text-muted);">
                    Failed to load appointments. Please try again.
                </td>
            </tr>
        `;
    }
}

async function handleBookAppointment(e) {
    e.preventDefault();

    const data = {
        doctor: document.getElementById('doctorName').value,
        specialization: document.getElementById('specialization').value,
        appointment_date: document.getElementById('appointmentDate').value,
        reason: document.getElementById('reason').value
    };

    try {
        await window.healthAssistant.bookAppointment(data);
        closeBookModal();
        document.getElementById('appointmentForm').reset();
        await loadAppointments();
    } catch (error) {
        console.error('Error booking appointment:', error);
    }
}

async function cancelAppointment(id) {
    if (!confirm('Are you sure you want to cancel this appointment?')) return;

    try {
        await window.healthAssistant.cancelAppointment(id);
        await loadAppointments();
    } catch (error) {
        console.error('Error cancelling appointment:', error);
    }
}

function openBookModal() {
    const modal = document.getElementById('bookModal');
    if (modal) {
        modal.style.display = 'flex';
        modal.classList.add('active');
    }
}

function closeBookModal() {
    const modal = document.getElementById('bookModal');
    if (modal) {
        modal.style.display = 'none';
        modal.classList.remove('active');
    }
}

window.addEventListener('click', function (event) {
    const modal = document.getElementById('bookModal');
    if (event.target === modal) closeBookModal();
});
