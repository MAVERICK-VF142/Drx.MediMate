// Admin Dashboard Functionality
import { getFirestore, collection, getDocs, doc, updateDoc, deleteDoc, addDoc } from "https://www.gstatic.com/firebasejs/10.11.1/firebase-firestore.js";
document.addEventListener('DOMContentLoaded', function() {
    loadDashboardData();
    fetchUsers();
    fetchAppointments();
    // Add calls for other features like fetchAppointments(), etc.
});

function loadDashboardData() {
    const userData = window.DashboardAuth.getUserData();
    document.getElementById('adminName').textContent = `${userData.firstName} ${userData.lastName}`;
    console.log('Loading admin dashboard for:', userData.firstName);
}

async function fetchUsers() {
    const db = getFirestore();
    const usersSnapshot = await getDocs(collection(db, "users"));
    const usersTableBody = document.querySelector('#usersTable tbody');
    usersTableBody.innerHTML = '';
    usersSnapshot.forEach((docSnapshot) => {
        const user = docSnapshot.data();
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${user.firstName} ${user.lastName}</td>
            <td>${user.email}</td>
            <td>${user.role}</td>
            <td>
                <button onclick="editUser('${docSnapshot.id}')">Edit</button>
                <button onclick="deleteUser('${docSnapshot.id}')">Delete</button>
            </td>
        `;
        usersTableBody.appendChild(row);
    });
}

async function editUser(userId) {
    // Implement edit modal or form
    // For example, prompt for new role
    const newRole = prompt('Enter new role:');
    if (newRole) {
        const db = getFirestore();
        await updateDoc(doc(db, "users", userId), { role: newRole });
        fetchUsers();
    }
}

async function deleteUser(userId) {
    if (confirm('Are you sure you want to delete this user?')) {
        const db = getFirestore();
        await deleteDoc(doc(db, "users", userId));
        fetchUsers();
    }
}

async function fetchAppointments() {
    const db = getFirestore();
    const apptsSnapshot = await getDocs(collection(db, "appointments"));
    const apptsTableBody = document.querySelector('#appointmentsTable tbody');
    apptsTableBody.innerHTML = '';
    apptsSnapshot.forEach((docSnapshot) => {
        const appt = docSnapshot.data();
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${appt.patientId}</td>
            <td>${appt.doctorId}</td>
            <td>${appt.date}</td>
            <td>
                <button onclick="editAppointment('${docSnapshot.id}')">Edit</button>
                <button onclick="deleteAppointment('${docSnapshot.id}')">Delete</button>
            </td>
        `;
        apptsTableBody.appendChild(row);
    });
}

async function addAppointment() {
    const patientId = prompt('Patient ID:');
    const doctorId = prompt('Doctor ID:');
    const date = prompt('Date:');
    if (patientId && doctorId && date) {
        const db = getFirestore();
        await addDoc(collection(db, "appointments"), { patientId, doctorId, date });
        fetchAppointments();
    }
}

async function editAppointment(apptId) {
    const newDate = prompt('New Date:');
    if (newDate) {
        const db = getFirestore();
        await updateDoc(doc(db, "appointments", apptId), { date: newDate });
        fetchAppointments();
    }
}

async function deleteAppointment(apptId) {
    if (confirm('Delete appointment?')) {
        const db = getFirestore();
        await deleteDoc(doc(db, "appointments", apptId));
        fetchAppointments();
    }
}
// Add similar functions for managing appointments, prescriptions, notifications, etc. 