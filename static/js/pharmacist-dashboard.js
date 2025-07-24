// Pharmacist Dashboard Functionality
document.addEventListener('DOMContentLoaded', function() {
    // Initialize dashboard features
    initializeInventoryManagement();
    initializePrescriptionProcessing();
    initializeReports();
    loadDashboardData();
});

function initializeInventoryManagement() {
    console.log('Pharmacist inventory management initialized');
    
    // Mock inventory data
    const inventoryData = [
        { name: 'Aspirin 325mg', stock: 150, expiry: '2025-06-15', supplier: 'PharmaCorp' },
        { name: 'Lisinopril 10mg', stock: 85, expiry: '2025-03-20', supplier: 'MediSupply' },
        { name: 'Metformin 500mg', stock: 45, expiry: '2024-12-10', supplier: 'HealthDist' },
        { name: 'Atorvastatin 20mg', stock: 120, expiry: '2025-08-30', supplier: 'PharmaCorp' }
    ];
    
    // Display inventory if container exists
    const inventoryContainer = document.getElementById('inventoryContainer');
    if (inventoryContainer) {
        displayInventory(inventoryData);
    }
    
    // Initialize inventory search
    const inventorySearch = document.getElementById('inventorySearch');
    if (inventorySearch) {
        inventorySearch.addEventListener('input', (e) => {
            filterInventory(inventoryData, e.target.value);
        });
    }
}

function initializePrescriptionProcessing() {
    console.log('Prescription processing system initialized');
    
    // Mock prescription queue
    const prescriptionQueue = [
        { id: 'RX001', patient: 'John Smith', medication: 'Lisinopril 10mg', quantity: 30, status: 'pending' },
        { id: 'RX002', patient: 'Mary Johnson', medication: 'Metformin 500mg', quantity: 60, status: 'in-progress' },
        { id: 'RX003', patient: 'Bob Wilson', medication: 'Aspirin 325mg', quantity: 90, status: 'ready' }
    ];
    
    // Display prescriptions if container exists
    const prescriptionContainer = document.getElementById('prescriptionQueue');
    if (prescriptionContainer) {
        displayPrescriptions(prescriptionQueue);
    }
}

function initializeReports() {
    console.log('Pharmacist reporting system initialized');
    
    // Mock sales data
    const salesData = [
        { date: '2024-01-15', revenue: 1250.50, prescriptions: 45 },
        { date: '2024-01-16', revenue: 980.75, prescriptions: 38 },
        { date: '2024-01-17', revenue: 1450.25, prescriptions: 52 }
    ];
    
    // Display reports if container exists
    const reportsContainer = document.getElementById('reportsContainer');
    if (reportsContainer) {
        displayReports(salesData);
    }
}

function displayInventory(data) {
    const container = document.getElementById('inventoryContainer');
    if (!container) return;
    
    container.innerHTML = `
        <h3>Current Inventory</h3>
        <div class="inventory-grid">
            ${data.map(item => `
                <div class="inventory-item ${item.stock < 50 ? 'low-stock' : ''}">
                    <h4>${item.name}</h4>
                    <p><strong>Stock:</strong> ${item.stock} units</p>
                    <p><strong>Expiry:</strong> ${item.expiry}</p>
                    <p><strong>Supplier:</strong> ${item.supplier}</p>
                    ${item.stock < 50 ? '<span class="alert">Low Stock!</span>' : ''}
                </div>
            `).join('')}
        </div>
    `;
}

function displayPrescriptions(data) {
    const container = document.getElementById('prescriptionQueue');
    if (!container) return;
    
    container.innerHTML = `
        <h3>Prescription Queue</h3>
        <div class="prescription-list">
            ${data.map(rx => `
                <div class="prescription-item status-${rx.status}">
                    <div class="rx-header">
                        <span class="rx-id">${rx.id}</span>
                        <span class="rx-status ${rx.status}">${rx.status}</span>
                    </div>
                    <p><strong>Patient:</strong> ${rx.patient}</p>
                    <p><strong>Medication:</strong> ${rx.medication}</p>
                    <p><strong>Quantity:</strong> ${rx.quantity}</p>
                    <button onclick="updatePrescriptionStatus('${rx.id}')" class="btn-process">
                        ${rx.status === 'pending' ? 'Start Processing' : 
                          rx.status === 'in-progress' ? 'Mark Ready' : 'Complete'}
                    </button>
                </div>
            `).join('')}
        </div>
    `;
}

function displayReports(data) {
    const container = document.getElementById('reportsContainer');
    if (!container) return;
    
    const totalRevenue = data.reduce((sum, day) => sum + day.revenue, 0);
    const totalPrescriptions = data.reduce((sum, day) => sum + day.prescriptions, 0);
    
    container.innerHTML = `
        <h3>Daily Reports</h3>
        <div class="reports-summary">
            <div class="summary-item">
                <h4>Total Revenue</h4>
                <p class="revenue">$${totalRevenue.toFixed(2)}</p>
            </div>
            <div class="summary-item">
                <h4>Total Prescriptions</h4>
                <p class="prescriptions">${totalPrescriptions}</p>
            </div>
        </div>
        <div class="daily-reports">
            ${data.map(day => `
                <div class="daily-report">
                    <h4>${day.date}</h4>
                    <p>Revenue: $${day.revenue.toFixed(2)}</p>
                    <p>Prescriptions: ${day.prescriptions}</p>
                </div>
            `).join('')}
        </div>
    `;
}

function filterInventory(data, searchTerm) {
    const filtered = data.filter(item => 
        item.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.supplier.toLowerCase().includes(searchTerm.toLowerCase())
    );
    displayInventory(filtered);
}

function updatePrescriptionStatus(rxId) {
    console.log(`Updating prescription status for ${rxId}`);
    // In a real app, this would make an API call
    alert(`Prescription ${rxId} status updated!`);
}

function loadDashboardData() {
    // Load pharmacist-specific data
    const userData = window.DashboardAuth?.getUserData() || {};
    console.log('Loading pharmacist dashboard for:', userData.firstName || 'Pharmacist');
    
    // Update welcome message
    const welcomeElement = document.getElementById('welcomeMessage');
    if (welcomeElement) {
        welcomeElement.textContent = `Welcome back, ${userData.firstName || 'Pharmacist'}!`;
    }
}

// Export functions for global access
window.PharmacistDashboard = {
    updatePrescriptionStatus,
    filterInventory,
    loadDashboardData
};
