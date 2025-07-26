// Admin Dashboard Functionality
import { getFirestore, collection, getDocs, doc, updateDoc, deleteDoc, addDoc } from "https://www.gstatic.com/firebasejs/10.11.1/firebase-firestore.js";
document.addEventListener('DOMContentLoaded', function() {
    loadDashboardData();
    fetchUsers();
    fetchAppointments();
    setupInvitationControls();
    fetchAdminInvitations();
    // Add calls for other features like fetchAppointments(), etc.
});

function loadDashboardData() {
    try {
        const userData = window.DashboardAuth.getUserData();
        
        // Validate that userData exists and required properties are strings
        if (!userData) {
            throw new Error('User data is undefined or null');
        }
        
        if (typeof userData.firstName !== 'string' || typeof userData.lastName !== 'string') {
            throw new Error('First name or last name is not a valid string');
        }
        
        document.getElementById('adminName').textContent = `${userData.firstName} ${userData.lastName}`;
        console.log('Loading admin dashboard for:', userData.firstName);
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        // Set a default value instead of failing completely
        document.getElementById('adminName').textContent = 'Admin User';
    }
}

async function fetchUsers() {
    const db = getFirestore();
    const usersTableBody = document.querySelector('#usersTable tbody');
    
    try {
        usersTableBody.innerHTML = '';
        const usersSnapshot = await getDocs(collection(db, "users"));
        
        usersSnapshot.forEach((docSnapshot) => {
            const user = docSnapshot.data();
            const row = document.createElement('tr');
            
            // Create and append cells safely using DOM methods
            const nameCell = document.createElement('td');
            nameCell.textContent = `${user.firstName} ${user.lastName}`;
            row.appendChild(nameCell);
            
            const emailCell = document.createElement('td');
            emailCell.textContent = user.email;
            row.appendChild(emailCell);
            
            const roleCell = document.createElement('td');
            roleCell.textContent = user.role;
            row.appendChild(roleCell);
            
            // Create actions cell
            const actionsCell = document.createElement('td');
            
            // Create edit button
            const editBtn = document.createElement('button');
            editBtn.textContent = 'Edit';
            editBtn.addEventListener('click', () => editUser(docSnapshot.id));
            actionsCell.appendChild(editBtn);
            
            // Add space between buttons
            actionsCell.appendChild(document.createTextNode(' '));
            
            // Create delete button
            const deleteBtn = document.createElement('button');
            deleteBtn.textContent = 'Delete';
            deleteBtn.addEventListener('click', () => deleteUser(docSnapshot.id));
            actionsCell.appendChild(deleteBtn);
            
            row.appendChild(actionsCell);
            
            usersTableBody.appendChild(row);
        });
    } catch (error) {
        console.error("Error fetching users:", error);
        // Display user-friendly error message
        const errorRow = document.createElement('tr');
        const errorCell = document.createElement('td');
        errorCell.colSpan = 4;
        errorCell.textContent = "Failed to load users. Please try again later.";
        errorRow.appendChild(errorCell);
        usersTableBody.appendChild(errorRow);
    }
}

async function editUser(userId) {
    try {
        // Implement edit modal or form
        // For example, prompt for new role
        const newRole = prompt('Enter new role:');
        
        // Validate the input
        if (!newRole || newRole.trim() === '') {
            alert('Role cannot be empty');
            return;
        }
        
        // Additional validation - restrict to valid role options
        const validRoles = ['admin', 'doctor', 'student', 'patient', 'pharmacist'];
        if (!validRoles.includes(newRole.toLowerCase())) {
            alert('Invalid role. Please enter: admin, doctor, student, patient, or pharmacist');
            return;
        }
        
        // Proceed with update
        const db = getFirestore();
        try {
            await updateDoc(doc(db, "users", userId), { role: newRole.toLowerCase() });
            alert('User role updated successfully');
            fetchUsers(); // Refresh the table
        } catch (updateError) {
            console.error("Database error updating user:", updateError);
            alert("Failed to update user role. Database error.");
        }
    } catch (error) {
        console.error("Error in edit user process:", error);
        alert("An unexpected error occurred while editing user.");
    }
}

async function deleteUser(userId) {
    try {
        if (confirm('Are you sure you want to delete this user?')) {
            const db = getFirestore();
            await deleteDoc(doc(db, "users", userId));
            fetchUsers();
        }
    } catch (error) {
        console.error("Error deleting user:", error);
        alert("Failed to delete user. Please try again.");
    }
}

async function fetchAppointments() {
    const db = getFirestore();
    const apptsTableBody = document.querySelector('#appointmentsTable tbody');
    
    try {
        // Clear the table body
        apptsTableBody.innerHTML = '';
        
        const apptsSnapshot = await getDocs(collection(db, "appointments"));
        
        apptsSnapshot.forEach((docSnapshot) => {
            const appt = docSnapshot.data();
            const row = document.createElement('tr');
            
            // Create and append cells safely
            const patientCell = document.createElement('td');
            patientCell.textContent = appt.patientId;
            row.appendChild(patientCell);
            
            const doctorCell = document.createElement('td');
            doctorCell.textContent = appt.doctorId;
            row.appendChild(doctorCell);
            
            const dateCell = document.createElement('td');
            dateCell.textContent = appt.date;
            row.appendChild(dateCell);
            
            // Create actions cell
            const actionsCell = document.createElement('td');
            
            // Create edit button
            const editBtn = document.createElement('button');
            editBtn.textContent = 'Edit';
            editBtn.addEventListener('click', () => editAppointment(docSnapshot.id));
            actionsCell.appendChild(editBtn);
            
            // Add space between buttons
            actionsCell.appendChild(document.createTextNode(' '));
            
            // Create delete button
            const deleteBtn = document.createElement('button');
            deleteBtn.textContent = 'Delete';
            deleteBtn.addEventListener('click', () => deleteAppointment(docSnapshot.id));
            actionsCell.appendChild(deleteBtn);
            
            row.appendChild(actionsCell);
            
            apptsTableBody.appendChild(row);
        });
    } catch (error) {
        console.error("Error fetching appointments:", error);
        // Display user-friendly error message
        const errorRow = document.createElement('tr');
        const errorCell = document.createElement('td');
        errorCell.colSpan = 4;
        errorCell.textContent = "Failed to load appointments. Please try again later.";
        errorRow.appendChild(errorCell);
        apptsTableBody.appendChild(errorRow);
    }
}

async function addAppointment() {
    try {
        const patientId = prompt('Patient ID:');
        const doctorId = prompt('Doctor ID:');
        const date = prompt('Date (YYYY-MM-DD):');
        
        // Input validation
        if (!patientId || patientId.trim() === '') {
            alert('Patient ID cannot be empty');
            return;
        }
        
        if (!doctorId || doctorId.trim() === '') {
            alert('Doctor ID cannot be empty');
            return;
        }
        
        // Validate date format (YYYY-MM-DD)
        const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
        if (!date || !dateRegex.test(date)) {
            alert('Please enter a valid date in YYYY-MM-DD format');
            return;
        }
        
        // Proceed with creating the appointment
        try {
            const db = getFirestore();
            await addDoc(collection(db, "appointments"), { 
                patientId: patientId.trim(), 
                doctorId: doctorId.trim(), 
                date 
            });
            alert('Appointment added successfully');
            fetchAppointments();
        } catch (dbError) {
            console.error("Database error adding appointment:", dbError);
            alert("Failed to add appointment. Database error occurred.");
        }
    } catch (error) {
        console.error("Error in add appointment process:", error);
        alert("An unexpected error occurred while adding the appointment.");
    }
}

async function editAppointment(apptId) {
    try {
        const newDate = prompt('New Date (YYYY-MM-DD):');
        
        // Input validation
        if (!newDate) {
            // User cancelled the prompt
            return;
        }
        
        // Validate date format (YYYY-MM-DD)
        const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
        if (!dateRegex.test(newDate.trim())) {
            alert('Please enter a valid date in YYYY-MM-DD format');
            return;
        }
        
        // Validate that the date is not in the past
        const selectedDate = new Date(newDate);
        const today = new Date();
        today.setHours(0, 0, 0, 0); // Reset time part for proper comparison
        
        if (selectedDate < today) {
            alert('Cannot schedule appointments in the past');
            return;
        }
        
        // Proceed with updating the appointment
        const db = getFirestore();
        try {
            await updateDoc(doc(db, "appointments", apptId), { date: newDate.trim() });
            alert('Appointment updated successfully');
            fetchAppointments(); // Refresh the table
        } catch (updateError) {
            console.error("Database error updating appointment:", updateError);
            alert("Failed to update appointment. Database error occurred.");
        }
    } catch (error) {
        console.error("Error in edit appointment process:", error);
        alert("An unexpected error occurred while editing the appointment.");
    }
}

async function deleteAppointment(apptId) {
    try {
        if (!apptId) {
            console.error("Invalid appointment ID provided");
            alert("Cannot delete appointment: Invalid ID");
            return;
        }
        
        if (confirm('Are you sure you want to delete this appointment?')) {
            const db = getFirestore();
            try {
                await deleteDoc(doc(db, "appointments", apptId));
                alert('Appointment deleted successfully');
                fetchAppointments(); // Refresh the table
            } catch (deleteError) {
                console.error("Database error deleting appointment:", deleteError);
                alert("Failed to delete appointment. Database error occurred.");
            }
        }
    } catch (error) {
        console.error("Error in delete appointment process:", error);
        alert("An unexpected error occurred while deleting the appointment.");
    }
}
// Add similar functions for managing appointments, prescriptions, notifications, etc. 

// Admin invitation management
function setupInvitationControls() {
    // Add the invitation section to the admin dashboard if it doesn't exist
    const mainContent = document.querySelector('.main-content');
    if (!document.getElementById('adminInvitationSection')) {
        const invitationSection = document.createElement('div');
        invitationSection.id = 'adminInvitationSection';
        invitationSection.className = 'dashboard-section';
        
        invitationSection.innerHTML = `
            <h2>Admin Invitations</h2>
            <div class="invite-controls">
                <input type="email" id="inviteEmail" placeholder="Email to invite" class="form-control" />
                <button id="createInviteBtn" class="btn btn-primary">Create Invitation</button>
            </div>
            <div class="table-responsive">
                <table class="data-table" id="invitationsTable">
                    <thead>
                        <tr>
                            <th>Email</th>
                            <th>Code</th>
                            <th>Created</th>
                            <th>Expires</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                    </tbody>
                </table>
            </div>
        `;
        
        // Insert after users section
        const usersSection = document.querySelector('.dashboard-section');
        if (usersSection) {
            usersSection.parentNode.insertBefore(invitationSection, usersSection.nextSibling);
        } else {
            mainContent.appendChild(invitationSection);
        }
        
        // Set up event listeners
        document.getElementById('createInviteBtn').addEventListener('click', createAdminInvitation);
    }
}

async function createAdminInvitation() {
    const email = document.getElementById('inviteEmail').value;
    
    if (!email || !validateEmail(email)) {
        alert('Please enter a valid email address');
        return;
    }
    
    try {
        const response = await fetch('/api/admin/invitation', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ email })
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert(`Invitation created! Code: ${data.invitation_code}`);
            document.getElementById('inviteEmail').value = '';
            fetchAdminInvitations();
        } else {
            alert(`Error: ${data.message}`);
        }
    } catch (error) {
        console.error('Error creating invitation:', error);
        alert('Failed to create invitation. Please try again.');
    }
}

async function fetchAdminInvitations() {
    try {
        const response = await fetch('/api/admin/invitations');
        const data = await response.json();
        
        if (data.success) {
            displayInvitations(data.invitations);
        } else {
            console.error('Failed to fetch invitations:', data.message);
        }
    } catch (error) {
        console.error('Error fetching invitations:', error);
    }
}

function displayInvitations(invitations) {
    const tableBody = document.querySelector('#invitationsTable tbody');
    tableBody.innerHTML = '';
    
    invitations.forEach(invitation => {
        const row = document.createElement('tr');
        
        // Format dates
        const createdDate = new Date(invitation.created_at).toLocaleString();
        const expiresDate = new Date(invitation.expires_at).toLocaleString();
        
        // Create cells
        const emailCell = document.createElement('td');
        emailCell.textContent = invitation.email;
        row.appendChild(emailCell);
        
        const codeCell = document.createElement('td');
        codeCell.textContent = invitation.code;
        row.appendChild(codeCell);
        
        const createdCell = document.createElement('td');
        createdCell.textContent = createdDate;
        row.appendChild(createdCell);
        
        const expiresCell = document.createElement('td');
        expiresCell.textContent = expiresDate;
        row.appendChild(expiresCell);
        
        const statusCell = document.createElement('td');
        statusCell.textContent = invitation.used ? 'Used' : 'Active';
        statusCell.className = invitation.used ? 'status-used' : 'status-active';
        row.appendChild(statusCell);
        
        const actionsCell = document.createElement('td');
        
        // Copy button
        const copyBtn = document.createElement('button');
        copyBtn.textContent = 'Copy Code';
        copyBtn.addEventListener('click', () => {
            navigator.clipboard.writeText(invitation.code)
                .then(() => alert('Code copied to clipboard!'))
                .catch(err => console.error('Failed to copy:', err));
        });
        actionsCell.appendChild(copyBtn);
        
        row.appendChild(actionsCell);
        tableBody.appendChild(row);
    });
}

function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
} 