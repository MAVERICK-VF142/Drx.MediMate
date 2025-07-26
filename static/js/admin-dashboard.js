// Admin Dashboard Functionality
import { getFirestore, collection, getDocs, getDoc, doc, updateDoc, deleteDoc, addDoc } from "https://www.gstatic.com/firebasejs/12.0.0/firebase-firestore.js";

// Valid user roles used across admin dashboard
const VALID_ROLES = ['admin', 'doctor', 'student', 'patient', 'pharmacist'];

// Utility: fetch user's full name by UID (falls back to UID if not found)
async function getUserNameById(uid) {
    try {
        const db = getFirestore();
        const userDoc = await getDoc(doc(db, "users", uid));
        if (userDoc.exists()) {
            const data = userDoc.data();
            return `${data.firstName ?? ''} ${data.lastName ?? ''}`.trim() || uid;
        }
    } catch (err) {
        console.error(`Error fetching user ${uid}:`, err);
    }
    return uid; // fallback
}document.addEventListener('DOMContentLoaded', function() {
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
        
        if (!VALID_ROLES.includes(newRole.toLowerCase())) {
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
        
        for (const docSnapshot of apptsSnapshot.docs) {
            const appt = docSnapshot.data();
            const row = document.createElement('tr');

            // Patient name cell
            const patientCell = document.createElement('td');
            patientCell.textContent = 'Loading...';
            row.appendChild(patientCell);

            // Doctor name cell
            const doctorCell = document.createElement('td');
            doctorCell.textContent = 'Loading...';
            row.appendChild(doctorCell);

            // Date cell
            const dateCell = document.createElement('td');
            dateCell.textContent = appt.date;
            row.appendChild(dateCell);

            // Asynchronously resolve names
            getUserNameById(appt.patientId).then(name => patientCell.textContent = name);
            getUserNameById(appt.doctorId).then(name => doctorCell.textContent = name);
            
            
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
        }
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
        const date = prompt('Date (DD-MM-YYYY):');
        
        // Input validation
        if (!patientId || patientId.trim() === '') {
            alert('Patient ID cannot be empty');
            return;
        }
        
        if (!doctorId || doctorId.trim() === '') {
            alert('Doctor ID cannot be empty');
            return;
        }
        
        // Validate date format (DD-MM-YYYY)
        const dateRegex = /^\d{2}-\d{2}-\d{4}$/;
        if (!date || !dateRegex.test(date)) {
            alert('Please enter a valid date in DD-MM-YYYY format');
            return;
        }

        // Parse and validate calendar date
        const [dayStr, monthStr, yearStr] = date.split('-');
        const year = Number(yearStr);
        const month = Number(monthStr) - 1; // JS months 0-11
        const day = Number(dayStr);
        const parsedDate = new Date(year, month, day);

        // Check if the constructed date matches the input (handles 2025-02-30)
        if (parsedDate.getFullYear() !== year || parsedDate.getMonth() !== month || parsedDate.getDate() !== day) {
            alert('Please enter a valid calendar date');
            return;
        }

        // Ensure date is not in the past
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        if (parsedDate < today) {
            alert('Cannot schedule appointments in the past');
            return;
        }
        
        // Check existence of patient and doctor IDs before creating the appointment
        try {
            const db = getFirestore();

            // Verify patient exists
            const patientDocRef = doc(db, "patients", patientId.trim());
            const patientSnap = await getDoc(patientDocRef);
            if (!patientSnap.exists()) {
                alert("Invalid Patient ID. No such patient found.");
                return;
            }

            // Verify doctor exists
            const doctorDocRef = doc(db, "doctors", doctorId.trim());
            const doctorSnap = await getDoc(doctorDocRef);
            if (!doctorSnap.exists()) {
                alert("Invalid Doctor ID. No such doctor found.");
                return;
            }

            // All good - create appointment
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
        const newDate = prompt('New Date (DD-MM-YYYY):');
        
        // Input validation
        if (!newDate) {
            // User cancelled the prompt
            return;
        }
        
        // Validate date format (DD-MM-YYYY)
        const dateRegex = /^\d{2}-\d{2}-\d{4}$/;
        if (!dateRegex.test(newDate.trim())) {
            alert('Please enter a valid date in DD-MM-YYYY format');
            return;
        }

        // Parse and validate calendar date
        const [dayStr, monthStr, yearStr] = newDate.trim().split('-');
        const year = Number(yearStr);
        const month = Number(monthStr) - 1;
        const day = Number(dayStr);
        const selectedDate = new Date(year, month, day);

        // Check for invalid calendar dates
        if (selectedDate.getFullYear() !== year || selectedDate.getMonth() !== month || selectedDate.getDate() !== day) {
            alert('Please enter a valid calendar date');
            return;
        }
        
        // Validate that the date is not in the past
        const today = new Date();
        today.setHours(0, 0, 0, 0);
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
        // Retrieve Firebase ID token for authenticated requests
        const currentUser = window.DashboardAuth?.getCurrentUser();
        const token = currentUser ? await currentUser.getIdToken() : null;

        const response = await fetch('/api/admin/invitation', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...(token ? { 'Authorization': `Bearer ${token}` } : {})
            },
            body: JSON.stringify({ email })
        });
        
        const data = await response.json();
        
        if (data.success) {
            try {
                await navigator.clipboard.writeText(data.invitation_code);
                alert('Invitation code copied to clipboard!');
            } catch (clipErr) {
                console.warn('Clipboard write failed:', clipErr);
                alert(`Invitation created! Code: ${data.invitation_code}`);
            }
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
        // Retrieve Firebase ID token for authenticated requests
        const currentUser = window.DashboardAuth?.getCurrentUser();
        const token = currentUser ? await currentUser.getIdToken() : null;
        
        const response = await fetch('/api/admin/invitations', {
            method: 'GET',
            headers: {
                ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
                'Content-Type': 'application/json'
            }
        });
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