// Student Dashboard Functionality
document.addEventListener('DOMContentLoaded', function() {
    // Initialize dashboard features
    initializeLearningTracking();
    initializeAssignmentManagement();
    initializeEducationalResources();
    loadDashboardData();
});

function initializeLearningTracking() {
    console.log('Student learning tracking initialized');
    
    // Mock course progress data
    const coursesData = [
        { id: 'C001', name: 'Pharmacology Basics', progress: 75, totalLessons: 20, completedLessons: 15 },
        { id: 'C002', name: 'Drug Interactions', progress: 45, totalLessons: 16, completedLessons: 7 },
        { id: 'C003', name: 'Clinical Pharmacy', progress: 90, totalLessons: 12, completedLessons: 11 },
        { id: 'C004', name: 'Pharmaceutical Calculations', progress: 60, totalLessons: 25, completedLessons: 15 }
    ];
    
    // Display courses if container exists
    const coursesContainer = document.getElementById('coursesContainer');
    if (coursesContainer) {
        displayCourses(coursesData);
    }
}

function initializeAssignmentManagement() {
    console.log('Assignment management initialized');
    
    // Mock assignments data
    const assignmentsData = [
        { id: 'A001', title: 'Drug Classification Essay', course: 'Pharmacology Basics', dueDate: '2024-01-25', status: 'pending' },
        { id: 'A002', title: 'Case Study Analysis', course: 'Clinical Pharmacy', dueDate: '2024-01-30', status: 'in-progress' },
        { id: 'A003', title: 'Dosage Calculations Quiz', course: 'Pharmaceutical Calculations', dueDate: '2024-02-05', status: 'not-started' },
        { id: 'A004', title: 'Interaction Report', course: 'Drug Interactions', dueDate: '2024-02-10', status: 'completed' }
    ];
    
    // Display assignments if container exists
    const assignmentsContainer = document.getElementById('assignmentsContainer');
    if (assignmentsContainer) {
        displayAssignments(assignmentsData);
    }
}

function initializeEducationalResources() {
    console.log('Educational resources initialized');
    
    // Mock resources data
    const resourcesData = [
        { id: 'R001', title: 'Pharmaceutical Reference Guide', type: 'PDF', category: 'Reference', size: '2.5 MB' },
        { id: 'R002', title: 'Drug Interaction Checker Tool', type: 'Interactive', category: 'Tool', size: 'Online' },
        { id: 'R003', title: 'Pharmacokinetics Video Series', type: 'Video', category: 'Learning', size: '1.2 GB' },
        { id: 'R004', title: 'Clinical Trial Database', type: 'Database', category: 'Research', size: 'Online' }
    ];
    
    // Display resources if container exists
    const resourcesContainer = document.getElementById('resourcesContainer');
    if (resourcesContainer) {
        displayResources(resourcesData);
    }
}

function displayCourses(data) {
    const container = document.getElementById('coursesContainer');
    if (!container) return;
    
    container.innerHTML = `
        <h3>My Courses</h3>
        <div class="courses-grid">
            ${data.map(course => `
                <div class="course-card">
                    <div class="course-header">
                        <h4>${course.name}</h4>
                        <span class="course-id">${course.id}</span>
                    </div>
                    <div class="progress-section">
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${course.progress}%"></div>
                        </div>
                        <span class="progress-text">${course.progress}% Complete</span>
                    </div>
                    <p>Lessons: ${course.completedLessons}/${course.totalLessons}</p>
                    <div class="course-actions">
                        <button onclick="continueCourse('${course.id}')" class="btn-continue">Continue Learning</button>
                        <button onclick="viewCourseDetails('${course.id}')" class="btn-details">View Details</button>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

function displayAssignments(data) {
    const container = document.getElementById('assignmentsContainer');
    if (!container) return;
    
    const sortedAssignments = data.sort((a, b) => new Date(a.dueDate) - new Date(b.dueDate));
    
    container.innerHTML = `
        <h3>My Assignments</h3>
        <div class="assignments-list">
            ${sortedAssignments.map(assignment => `
                <div class="assignment-item status-${assignment.status}">
                    <div class="assignment-header">
                        <h4>${assignment.title}</h4>
                        <span class="assignment-status ${assignment.status}">${assignment.status.replace('-', ' ')}</span>
                    </div>
                    <p><strong>Course:</strong> ${assignment.course}</p>
                    <p><strong>Due Date:</strong> ${assignment.dueDate}</p>
                    <div class="assignment-actions">
                        ${assignment.status === 'completed' 
                            ? '<button onclick="viewSubmission(\'' + assignment.id + '\')" class="btn-view">View Submission</button>'
                            : '<button onclick="startAssignment(\'' + assignment.id + '\')" class="btn-start">Start Assignment</button>'
                        }
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

function displayResources(data) {
    const container = document.getElementById('resourcesContainer');
    if (!container) return;
    
    container.innerHTML = `
        <h3>Educational Resources</h3>
        <div class="resources-grid">
            ${data.map(resource => `
                <div class="resource-card">
                    <div class="resource-icon ${resource.type.toLowerCase()}">
                        ${getResourceIcon(resource.type)}
                    </div>
                    <div class="resource-info">
                        <h4>${resource.title}</h4>
                        <p><strong>Type:</strong> ${resource.type}</p>
                        <p><strong>Category:</strong> ${resource.category}</p>
                        <p><strong>Size:</strong> ${resource.size}</p>
                    </div>
                    <div class="resource-actions">
                        <button onclick="accessResource('${resource.id}')" class="btn-access">Access</button>
                        <button onclick="downloadResource('${resource.id}')" class="btn-download">Download</button>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

function getResourceIcon(type) {
    const icons = {
        'PDF': '📄',
        'Video': '🎥',
        'Interactive': '🔧',
        'Database': '🗃️'
    };
    return icons[type] || '📚';
}

function continueCourse(courseId) {
    console.log(`Continuing course ${courseId}`);
    alert(`Opening course ${courseId} - Continue Learning`);
}

function viewCourseDetails(courseId) {
    console.log(`Viewing details for course ${courseId}`);
    alert(`Opening detailed view for course ${courseId}`);
}

function startAssignment(assignmentId) {
    console.log(`Starting assignment ${assignmentId}`);
    alert(`Opening assignment ${assignmentId} for completion`);
}

function viewSubmission(assignmentId) {
    console.log(`Viewing submission for assignment ${assignmentId}`);
    alert(`Opening submission details for assignment ${assignmentId}`);
}

function accessResource(resourceId) {
    console.log(`Accessing resource ${resourceId}`);
    alert(`Opening resource ${resourceId}`);
}

function downloadResource(resourceId) {
    console.log(`Downloading resource ${resourceId}`);
    alert(`Starting download for resource ${resourceId}`);
}

function loadDashboardData() {
    // Load student-specific data
    const userData = window.DashboardAuth?.getUserData() || {};
    console.log('Loading student dashboard for:', userData.firstName || 'Student');
    
    // Update welcome message
    const welcomeElement = document.getElementById('welcomeMessage');
    if (welcomeElement) {
        welcomeElement.textContent = `Welcome back, ${userData.firstName || 'Student'}!`;
    }
    
    // Display institution if available
    const institutionElement = document.getElementById('institutionName');
    if (institutionElement && userData.institution) {
        institutionElement.textContent = userData.institution;
    }
}

// Export functions for global access
window.StudentDashboard = {
    continueCourse,
    viewCourseDetails,
    startAssignment,
    viewSubmission,
    accessResource,
    downloadResource,
    loadDashboardData
};
