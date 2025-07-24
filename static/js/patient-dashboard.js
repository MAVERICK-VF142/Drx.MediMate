// Patient Dashboard Functionality
document.addEventListener('DOMContentLoaded', function() {
    // Initialize dashboard features
    initializeMedicationTracking();
    initializeHealthReminders();
    initializeAppointments();
    loadDashboardData();
});

function initializeMedicationTracking() {
    console.log('Patient medication tracking initialized');
    
    // Mock medication data
    const medicationsData = [
        { id: 'M001', name: 'Lisinopril 10mg', frequency: 'Once daily', nextDose: '8:00 AM', remaining: 25 },
        { id: 'M002', name: 'Metformin 500mg', frequency: 'Twice daily', nextDose: '12:00 PM', remaining: 45 },
        { id: 'M003', name: 'Aspirin 81mg', frequency: 'Once daily', nextDose: '8:00 AM', remaining: 60 },
        { id: 'M004', name: 'Atorvastatin 20mg', frequency: 'Once daily', nextDose: '10:00 PM', remaining: 15 }
    ];
    
    // Display medications if container exists
    const medicationsContainer = document.getElementById('medicationsContainer');
    if (medicationsContainer) {
        displayMedications(medicationsData);
    }
}

function initializeHealthReminders() {
    console.log('Health reminder system initialized');
    
    // Mock reminders data
    const remindersData = [
        { id: 'R001', title: 'Take Lisinopril', time: '08:00', type: 'medication', status: 'pending' },
        { id: 'R002', title: 'Doctor Appointment', time: '14:30', type: 'appointment', status: 'upcoming' },
        { id: 'R003', title: 'Blood Pressure Check', time: '09:00', type: 'health-check', status: 'pending' },
        { id: 'R004', title: 'Take Metformin', time: '12:00', type: 'medication', status: 'completed' }
    ];
    
    // Display reminders if container exists
    const remindersContainer = document.getElementById('remindersContainer');
    if (remindersContainer) {
        displayReminders(remindersData);
    }
}

function initializeAppointments() {
    console.log('Patient appointments initialized');
    
    // Mock appointments data
    const appointmentsData = [
        { id: 'A001', doctor: 'Dr. Smith', specialty: 'Cardiologist', date: '2024-01-25', time: '2:30 PM', status: 'confirmed' },
        { id: 'A002', doctor: 'Dr. Johnson', specialty: 'General Practitioner', date: '2024-02-10', time: '10:00 AM', status: 'pending' },
        { id: 'A003', doctor: 'Dr. Brown', specialty: 'Endocrinologist', date: '2024-02-20', time: '3:00 PM', status: 'confirmed' }
    ];
    
    // Display appointments if container exists
    const appointmentsContainer = document.getElementById('appointmentsContainer');
    if (appointmentsContainer) {
        displayAppointments(appointmentsData);
    }
}

function displayMedications(data) {
    const container = document.getElementById('medicationsContainer');
    if (!container) return;
    
    container.innerHTML = `
        <h3>My Medications</h3>
        <div class="medications-grid">
            ${data.map(med => `
                <div class="medication-card ${med.remaining < 20 ? 'low-supply' : ''}">
                    <div class="medication-header">
                        <h4>${med.name}</h4>
                        <span class="med-id">${med.id}</span>
                    </div>
                    <p><strong>Frequency:</strong> ${med.frequency}</p>
                    <p><strong>Next Dose:</strong> ${med.nextDose}</p>
                    <p><strong>Remaining:</strong> ${med.remaining} pills</p>
                    ${med.remaining < 20 ? '<span class="alert">Refill Soon!</span>' : ''}
                    <div class="medication-actions">
                        <button onclick="takeMedication('${med.id}')" class="btn-take">Mark as Taken</button>
                        <button onclick="setReminder('${med.id}')" class="btn-reminder">Set Reminder</button>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

function displayReminders(data) {
    const container = document.getElementById('remindersContainer');
    if (!container) return;
    
    const todayReminders = data.filter(reminder => reminder.status !== 'completed');
    
    container.innerHTML = `
        <h3>Today's Reminders</h3>
        <div class="reminders-list">
            ${todayReminders.map(reminder => `
                <div class="reminder-item ${reminder.status}">
                    <div class="reminder-icon ${reminder.type}">
                        ${getReminderIcon(reminder.type)}
                    </div>
                    <div class="reminder-content">
                        <h4>${reminder.title}</h4>
                        <p><strong>Time:</strong> ${reminder.time}</p>
                        <span class="reminder-type">${reminder.type.replace('-', ' ')}</span>
                    </div>
                    <div class="reminder-actions">
                        <button onclick="completeReminder('${reminder.id}')" class="btn-complete">Complete</button>
                        <button onclick="snoozeReminder('${reminder.id}')" class="btn-snooze">Snooze</button>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

function displayAppointments(data) {
    const container = document.getElementById('appointmentsContainer');
    if (!container) return;
    
    const upcomingAppointments = data.sort((a, b) => new Date(a.date) - new Date(b.date));
    
    container.innerHTML = `
        <h3>Upcoming Appointments</h3>
        <div class="appointments-list">
            ${upcomingAppointments.map(appointment => `
                <div class="appointment-item status-${appointment.status}">
                    <div class="appointment-header">
                        <h4>${appointment.doctor}</h4>
                        <span class="appointment-status ${appointment.status}">${appointment.status}</span>
                    </div>
                    <p><strong>Specialty:</strong> ${appointment.specialty}</p>
                    <p><strong>Date:</strong> ${appointment.date}</p>
                    <p><strong>Time:</strong> ${appointment.time}</p>
                    <div class="appointment-actions">
                        <button onclick="confirmAppointment('${appointment.id}')" class="btn-confirm">
                            ${appointment.status === 'confirmed' ? 'View Details' : 'Confirm'}
                        </button>
                        <button onclick="rescheduleAppointment('${appointment.id}')" class="btn-reschedule">Reschedule</button>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

function getReminderIcon(type) {
    const icons = {
        'medication': '💊',
        'appointment': '📅',
        'health-check': '🩺'
    };
    return icons[type] || '⏰';
}

function takeMedication(medId) {
    console.log(`Marking medication ${medId} as taken`);
    alert(`Medication ${medId} marked as taken!`);
    // In a real app, this would update the medication log
}

function setReminder(medId) {
    console.log(`Setting reminder for medication ${medId}`);
    alert(`Reminder set for medication ${medId}`);
}

function completeReminder(reminderId) {
    console.log(`Completing reminder ${reminderId}`);
    alert(`Reminder ${reminderId} completed!`);
    // In a real app, this would update the reminder status
}

function snoozeReminder(reminderId) {
    console.log(`Snoozing reminder ${reminderId}`);
    alert(`Reminder ${reminderId} snoozed for 15 minutes`);
}

function confirmAppointment(appointmentId) {
    console.log(`Confirming appointment ${appointmentId}`);
    alert(`Appointment ${appointmentId} confirmed!`);
}

function rescheduleAppointment(appointmentId) {
    console.log(`Rescheduling appointment ${appointmentId}`);
    alert(`Opening rescheduling options for appointment ${appointmentId}`);
}

function loadDashboardData() {
    // Load patient-specific data
    const userData = window.DashboardAuth?.getUserData() || {};
    console.log('Loading patient dashboard for:', userData.firstName || 'Patient');
    
    // Update welcome message
    const welcomeElement = document.getElementById('welcomeMessage');
    if (welcomeElement) {
        welcomeElement.textContent = `Welcome back, ${userData.firstName || 'Patient'}!`;
    }
    
    // Display health summary
    displayHealthSummary(userData);
}

function displayHealthSummary(userData) {
    const summaryContainer = document.getElementById('healthSummary');
    if (!summaryContainer) return;
    
    // Mock health data
    const healthData = {
        lastCheckup: '2024-01-15',
        bloodPressure: '120/80',
        weight: '70 kg',
        allergies: userData.allergies || ['None known']
    };
    
    summaryContainer.innerHTML = `
        <h3>Health Summary</h3>
        <div class="health-stats">
            <div class="health-stat">
                <h4>Last Checkup</h4>
                <p>${healthData.lastCheckup}</p>
            </div>
            <div class="health-stat">
                <h4>Blood Pressure</h4>
                <p>${healthData.bloodPressure}</p>
            </div>
            <div class="health-stat">
                <h4>Weight</h4>
                <p>${healthData.weight}</p>
            </div>
            <div class="health-stat">
                <h4>Allergies</h4>
                <p>${healthData.allergies.join(', ')}</p>
            </div>
        </div>
    `;
}

// Export functions for global access
window.PatientDashboard = {
    takeMedication,
    setReminder,
    completeReminder,
    snoozeReminder,
    confirmAppointment,
    rescheduleAppointment,
    loadDashboardData
};
