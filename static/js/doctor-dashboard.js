// Enhanced Doctor Dashboard Functionality
document.addEventListener('DOMContentLoaded', function() {
    // Initialize dashboard features
    initializePatientManagement();
    initializeAppointmentScheduler();
    initializePrescriptionTools();
    initializeNotifications();
    loadDashboardData();
    updateStats();
});

function initializePatientManagement() {
    console.log('Doctor patient management initialized');
    
    // Enhanced patient data with more details
    const patientsData = [
        { 
            id: 'P001', 
            name: 'Alice Brown', 
            age: 45, 
            condition: 'Hypertension', 
            lastVisit: '2024-01-18',
            status: 'active',
            phone: '+1 (555) 123-4567',
            email: 'alice.brown@email.com',
            nextAppointment: '2024-01-25',
            riskLevel: 'Medium'
        },
        { 
            id: 'P002', 
            name: 'David Lee', 
            age: 62, 
            condition: 'Diabetes Type 2', 
            lastVisit: '2024-01-15',
            status: 'critical',
            phone: '+1 (555) 234-5678',
            email: 'david.lee@email.com',
            nextAppointment: '2024-01-22',
            riskLevel: 'High'
        },
        { 
            id: 'P003', 
            name: 'Sarah Wilson', 
            age: 38, 
            condition: 'Asthma', 
            lastVisit: '2024-01-20',
            status: 'active',
            phone: '+1 (555) 345-6789',
            email: 'sarah.wilson@email.com',
            nextAppointment: '2024-02-05',
            riskLevel: 'Low'
        },
        { 
            id: 'P004', 
            name: 'Michael Chen', 
            age: 55, 
            condition: 'High Cholesterol', 
            lastVisit: '2024-01-10',
            status: 'inactive',
            phone: '+1 (555) 456-7890',
            email: 'michael.chen@email.com',
            nextAppointment: null,
            riskLevel: 'Medium'
        },
        { 
            id: 'P005', 
            name: 'Emma Davis', 
            age: 29, 
            condition: 'Anxiety', 
            lastVisit: '2024-01-19',
            status: 'active',
            phone: '+1 (555) 567-8901',
            email: 'emma.davis@email.com',
            nextAppointment: '2024-01-28',
            riskLevel: 'Low'
        }
    ];
    
    // Store globally for filtering
    window.allPatients = patientsData;
    
    // Display patients
    displayPatients(patientsData);
}

function initializeAppointmentScheduler() {
    console.log('Appointment scheduler initialized');
    
    // Enhanced appointments data
    const appointmentsData = [
        { 
            id: 'A001', 
            patient: 'John Smith', 
            time: '09:00', 
            duration: '30 min',
            date: '2024-01-20', 
            type: 'consultation',
            status: 'confirmed',
            notes: 'Follow-up for blood pressure medication'
        },
        { 
            id: 'A002', 
            patient: 'Emma Davis', 
            time: '10:30', 
            duration: '45 min',
            date: '2024-01-20', 
            type: 'consultation',
            status: 'confirmed',
            notes: 'Initial consultation for anxiety symptoms'
        },
        { 
            id: 'A003', 
            patient: 'Robert Johnson', 
            time: '14:00', 
            duration: '30 min',
            date: '2024-01-20', 
            type: 'follow-up',
            status: 'confirmed',
            notes: 'Diabetes management review'
        },
        { 
            id: 'A004', 
            patient: 'Lisa Anderson', 
            time: '15:30', 
            duration: '30 min',
            date: '2024-01-20', 
            type: 'follow-up',
            status: 'pending',
            notes: 'Post-surgery check-up'
        },
        { 
            id: 'A005', 
            patient: 'David Lee', 
            time: '16:30', 
            duration: '60 min',
            date: '2024-01-20', 
            type: 'emergency',
            status: 'urgent',
            notes: 'Emergency consultation for chest pain'
        }
    ];
    
    displayAppointments(appointmentsData);
}

function initializePrescriptionTools() {
    console.log('Prescription tools initialized');
    
    // Enhanced prescriptions data
    const recentPrescriptions = [
        { 
            id: 'RX001', 
            patient: 'Alice Brown', 
            medications: ['Lisinopril 10mg', 'Hydrochlorothiazide 25mg'], 
            date: '2024-01-18',
            status: 'Active',
            refills: 2,
            pharmacist: 'Dr. Johnson Pharmacy'
        },
        { 
            id: 'RX002', 
            patient: 'David Lee', 
            medications: ['Metformin 500mg', 'Glipizide 5mg'], 
            date: '2024-01-17',
            status: 'Active',
            refills: 1,
            pharmacist: 'MediCare Pharmacy'
        },
        { 
            id: 'RX003', 
            patient: 'Sarah Wilson', 
            medications: ['Albuterol Inhaler', 'Fluticasone Inhaler'], 
            date: '2024-01-15',
            status: 'Completed',
            refills: 0,
            pharmacist: 'HealthFirst Pharmacy'
        },
        { 
            id: 'RX004', 
            patient: 'Emma Davis', 
            medications: ['Sertraline 50mg'], 
            date: '2024-01-19',
            status: 'Active',
            refills: 3,
            pharmacist: 'City Pharmacy'
        }
    ];
    
    displayRecentPrescriptions(recentPrescriptions);
}

function initializeNotifications() {
    console.log('Notifications system initialized');
    
    const notificationsData = [
        {
            id: 'N001',
            type: 'warning',
            title: 'Critical Patient Alert',
            message: 'David Lee\'s blood sugar levels are critically high',
            time: '2 minutes ago',
            unread: true
        },
        {
            id: 'N002',
            type: 'info',
            title: 'Appointment Reminder',
            message: 'Emma Davis appointment in 30 minutes',
            time: '28 minutes ago',
            unread: true
        },
        {
            id: 'N003',
            type: 'success',
            title: 'Prescription Filled',
            message: 'Alice Brown\'s prescription has been filled',
            time: '1 hour ago',
            unread: true
        },
        {
            id: 'N004',
            type: 'info',
            title: 'Lab Results Available',
            message: 'Blood work results for 3 patients are ready',
            time: '2 hours ago',
            unread: false
        },
        {
            id: 'N005',
            type: 'info',
            title: 'Schedule Update',
            message: 'Tomorrow\'s schedule has been updated',
            time: '3 hours ago',
            unread: false
        }
    ];
    
    displayNotifications(notificationsData);
}

function displayPatients(data) {
    const container = document.getElementById('patientsContainer');
    if (!container) return;
    
    if (data.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">
                    <i class="fas fa-users"></i>
                </div>
                <h3>No patients found</h3>
                <p>Try adjusting your search or filter criteria</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = data.map(patient => `
        <div class="patient-item" onclick="viewPatientDetails('${patient.id}')">
            <div class="patient-header">
                <div class="patient-info">
                    <h4>${patient.name}</h4>
                    <div class="patient-meta">${patient.age} years • ${patient.condition}</div>
                </div>
                <span class="patient-status ${patient.status}">${patient.status}</span>
            </div>
            <div class="patient-details">
                <div class="patient-detail">
                    <strong>Last Visit:</strong><br>${patient.lastVisit}
                </div>
                <div class="patient-detail">
                    <strong>Risk Level:</strong><br>${patient.riskLevel}
                </div>
                <div class="patient-detail">
                    <strong>Next Appointment:</strong><br>${patient.nextAppointment || 'Not scheduled'}
                </div>
                <div class="patient-detail">
                    <strong>Contact:</strong><br>${patient.phone}
                </div>
            </div>
            <div class="patient-actions">
                <button class="btn-sm btn-primary" onclick="event.stopPropagation(); viewPatientHistory('${patient.id}')">
                    <i class="fas fa-history"></i> History
                </button>
                <button class="btn-sm btn-secondary" onclick="event.stopPropagation(); scheduleAppointment('${patient.id}')">
                    <i class="fas fa-calendar"></i> Schedule
                </button>
                <button class="btn-sm btn-success" onclick="event.stopPropagation(); createPrescription('${patient.id}')">
                    <i class="fas fa-prescription"></i> Prescribe
                </button>
            </div>
        </div>
    `).join('');
}

function displayAppointments(data) {
    const container = document.getElementById('appointmentsContainer');
    if (!container) return;
    
    if (data.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">
                    <i class="fas fa-calendar"></i>
                </div>
                <h3>No appointments today</h3>
                <p>Your schedule is clear for today</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = data.map(appointment => `
        <div class="appointment-item" onclick="viewAppointmentDetails('${appointment.id}')">
            <div class="appointment-time">
                <span class="time">${appointment.time}</span>
                <span class="duration">${appointment.duration}</span>
            </div>
            <div class="appointment-details">
                <h4>${appointment.patient}</h4>
                <p>${appointment.notes}</p>
                <span class="appointment-type ${appointment.type}">${appointment.type}</span>
            </div>
        </div>
    `).join('');
}

function displayRecentPrescriptions(data) {
    const container = document.getElementById('prescriptionsContainer');
    if (!container) return;
    
    if (data.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">
                    <i class="fas fa-prescription-bottle-alt"></i>
                </div>
                <h3>No recent prescriptions</h3>
                <p>Prescriptions you create will appear here</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = data.map(rx => `
        <div class="prescription-item" onclick="viewPrescriptionDetails('${rx.id}')">
            <div class="prescription-header">
                <span class="prescription-id">${rx.id}</span>
                <span class="prescription-date">${rx.date}</span>
            </div>
            <div class="prescription-content">
                <h5>${rx.patient}</h5>
                <p><strong>Status:</strong> ${rx.status} • <strong>Refills:</strong> ${rx.refills}</p>
                <div class="prescription-medications">
                    <strong>Medications:</strong> ${rx.medications.join(', ')}
                </div>
            </div>
        </div>
    `).join('');
}

function displayNotifications(data) {
    const container = document.getElementById('notificationsContainer');
    if (!container) return;
    
    if (data.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">
                    <i class="fas fa-bell"></i>
                </div>
                <h3>No notifications</h3>
                <p>You're all caught up!</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = data.map(notification => `
        <div class="notification-item ${notification.unread ? 'unread' : ''}" onclick="markAsRead('${notification.id}')">
            <div class="notification-icon ${notification.type}">
                <i class="fas fa-${notification.type === 'warning' ? 'exclamation-triangle' : notification.type === 'success' ? 'check-circle' : 'info-circle'}"></i>
            </div>
            <div class="notification-content">
                <h5>${notification.title}</h5>
                <p>${notification.message}</p>
                <span class="notification-time">${notification.time}</span>
            </div>
        </div>
    `).join('');
}

function updateStats() {
    // Update dashboard statistics
    const stats = {
        totalPatients: window.allPatients ? window.allPatients.length : 247,
        todayAppointments: 8,
        totalPrescriptions: 156,
        consultationsToday: 5
    };
    
    document.getElementById('totalPatients').textContent = stats.totalPatients;
    document.getElementById('todayAppointments').textContent = stats.todayAppointments;
    document.getElementById('totalPrescriptions').textContent = stats.totalPrescriptions;
    document.getElementById('consultationsToday').textContent = stats.consultationsToday;
}

// Filter functions
function filterPatients() {
    const searchTerm = document.getElementById('patientSearch').value.toLowerCase();
    const filterValue = document.getElementById('patientFilter').value;
    
    if (!window.allPatients) return;
    
    let filtered = window.allPatients.filter(patient => {
        const matchesSearch = patient.name.toLowerCase().includes(searchTerm) ||
                            patient.condition.toLowerCase().includes(searchTerm) ||
                            patient.id.toLowerCase().includes(searchTerm);
        
        const matchesFilter = filterValue === 'all' || patient.status === filterValue;
        
        return matchesSearch && matchesFilter;
    });
    
    displayPatients(filtered);
}

// Event handlers
function viewPatientDetails(patientId) {
    console.log(`Viewing details for patient ${patientId}`);
    alert(`Opening detailed patient profile for ${patientId}`);
}

function viewPatientHistory(patientId) {
    console.log(`Viewing history for patient ${patientId}`);
    alert(`Opening medical history for patient ${patientId}`);
}

function scheduleAppointment(patientId) {
    console.log(`Scheduling appointment for patient ${patientId}`);
    alert(`Opening appointment scheduler for patient ${patientId}`);
}

function createPrescription(patientId) {
    console.log(`Creating prescription for patient ${patientId}`);
    alert(`Opening prescription creation for patient ${patientId}`);
}

function viewAppointmentDetails(appointmentId) {
    console.log(`Viewing appointment details ${appointmentId}`);
    alert(`Opening appointment details for ${appointmentId}`);
}

function viewPrescriptionDetails(rxId) {
    console.log(`Viewing prescription ${rxId}`);
    alert(`Opening prescription details for ${rxId}`);
}

function markAsRead(notificationId) {
    console.log(`Marking notification ${notificationId} as read`);
    const notificationItem = event.currentTarget;
    notificationItem.classList.remove('unread');
    
    // Update notification count
    const currentCount = parseInt(document.getElementById('notificationCount').textContent);
    if (currentCount > 0) {
        document.getElementById('notificationCount').textContent = currentCount - 1;
    }
}

function loadDashboardData() {
    // Load doctor-specific data
    const userData = window.DashboardAuth?.getUserData() || {};
    console.log('Loading doctor dashboard for:', userData.firstName || 'Doctor');
    
    // Update welcome message if element exists on other pages
    const welcomeElement = document.getElementById('welcomeMessage');
    if (welcomeElement && welcomeElement.tagName !== 'P') {
        welcomeElement.textContent = `Welcome back, Dr. ${userData.lastName || userData.firstName || 'Doctor'}!`;
    }
}

// Export functions for global access
window.DoctorDashboard = {
    viewPatientHistory,
    scheduleAppointment,
    createPrescription,
    viewAppointmentDetails,
    viewPrescriptionDetails,
    filterPatients,
    loadDashboardData
};
