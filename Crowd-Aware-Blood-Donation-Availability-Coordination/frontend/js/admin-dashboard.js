document.addEventListener('DOMContentLoaded', function () {
    // Logout handler - attached early
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function (e) {
            e.preventDefault();
            localStorage.clear();
            window.location.href = 'login.html';
        });
    }

    // Role Check
    const role = localStorage.getItem('role');
    if (role !== 'admin') {
        alert('Unauthorized access');
        window.location.href = 'login.html';
        return;
    }

    // Tab Logic

    // Tab Logic
    // Expose switchTab globally
    window.switchTab = function (tabId) {
        // Remove active class from all tabs and buttons
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));

        // Activate target tab and button
        const targetTab = document.getElementById(tabId);
        if (targetTab) targetTab.classList.add('active');

        // Find the button that calls this function (tricky without event, so we use logic or just leave button active state management to the user click)
        // Actually, we can just find the button by its onclick attribute or text, but better to match by logic
        // For simplicity:
        const btns = document.querySelectorAll('.nav-btn');
        btns.forEach(btn => {
            if (btn.getAttribute('onclick').includes(tabId)) {
                btn.classList.add('active');
            }
        });

        if (tabId === 'analytics') {
            loadAnalytics();
        }
    };

    // Initialize defaults if needed
    // (default active tab is set in HTML)


    // Filter Logic
    const filterSelect = document.getElementById('verificationFilter');
    if (filterSelect) {
        filterSelect.addEventListener('change', () => {
            loadAllVerifications();
        });
    }

    // Load Initial Data
    loadAllVerifications();
    loadBloodRequests();
    loadTotalDonors();

    // Run AI Prediction
    const predBtn = document.getElementById('runPredictionBtn');
    if (predBtn) {
        predBtn.addEventListener('click', function () {
            predBtn.disabled = true;
            predBtn.innerHTML = '<span class="icon">⏳</span> Analyzing...';

            fetch('/api/analytics/run-prediction', { method: 'POST' })
                .then(res => res.json())
                .then(data => {
                    const shorts = data.details.filter(d => d.includes('Shortage')).length;
                    alert(`${data.message}\nShortages Detected: ${shorts}\nRecommendations: ${data.details.filter(d => d.includes('Camp')).length}`);
                })
                .catch(err => alert('Analysis failed'))
                .finally(() => {
                    predBtn.disabled = false;
                    predBtn.innerHTML = '<span class="icon">🔮</span> AI Analysis';
                });
        });
    }
});

function loadTotalDonors() {
    fetch('/api/users?role=donor')
        .then(res => res.json())
        .then(users => {
            const el = document.getElementById('totalDonorsCount');
            if (el) el.textContent = users.length;
        })
        .catch(err => console.error('Error loading donors:', err));
}

const dashboardStats = {
    donors: 0,
    hospitals: 0,
    banks: 0
};

function updateGlobalStats() {
    const totalPending = dashboardStats.donors + dashboardStats.hospitals + dashboardStats.banks;
    const pendingElement = document.getElementById('pendingCount');
    if (pendingElement) pendingElement.textContent = totalPending;
}

// ... existing functions ...

let collectionChartInstance = null;
let distributionChartInstance = null;

function loadAnalytics() {
    // 1. Monthly Trends
    fetch('/api/analytics/monthly')
        .then(res => res.json())
        .then(data => {
            const ctx = document.getElementById('collectionChart').getContext('2d');

            if (collectionChartInstance) collectionChartInstance.destroy();

            collectionChartInstance = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Units Collected',
                        data: data.data,
                        borderColor: '#e74c3c',
                        backgroundColor: 'rgba(231, 76, 60, 0.2)',
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: { responsive: true }
            });
        });

    // 2. Blood Group Distribution
    fetch('/api/analytics/distribution')
        .then(res => res.json())
        .then(data => {
            const ctx = document.getElementById('distributionChart').getContext('2d');

            if (distributionChartInstance) distributionChartInstance.destroy();

            distributionChartInstance = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: data.labels,
                    datasets: [{
                        data: data.data,
                        backgroundColor: [
                            '#e74c3c', '#3498db', '#9b59b6', '#f1c40f',
                            '#e67e22', '#2ecc71', '#34495e', '#95a5a6'
                        ]
                    }]
                },
                options: { responsive: true }
            });
        });
}

function loadAllVerifications() {
    loadReports(); // Donors Tab
    loadUsers('hospital', 'hospitalsList'); // Hospitals Tab
    loadUsers('blood_bank', 'banksList'); // Banks Tab
}

function loadReports() {
    const list = document.getElementById('reportsList');
    const statusFilter = document.getElementById('verificationFilter').value;
    list.innerHTML = '<p>Loading...</p>';

    fetch('/api/reports')
        .then(response => response.json())
        .then(reports => {
            list.innerHTML = '';

            // Calculate pending for stats regardless of filter
            const pendingCount = reports.filter(r => r.status === 'pending').length;
            dashboardStats.donors = pendingCount;
            updateGlobalStats();
            // document.querySelector('.stat-number:not(#pendingCount)').textContent = reports.length; // Approximate "Total Donors"

            // Filter for display
            const filteredReports = reports.filter(r => {
                if (statusFilter === 'all') return true;
                return r.status === statusFilter;
            });

            if (filteredReports.length === 0) {
                list.innerHTML = '<p>No reports found.</p>';
                return;
            }

            let pending = 0;

            filteredReports.forEach(report => {
                if (report.status === 'pending') pending++;

                const card = document.createElement('div');
                card.className = 'report-card';
                card.innerHTML = `
                <div class="report-info">
                    <h4>${report.donor_name}</h4>
                    <div class="report-meta">
                        <p><strong>Type:</strong> Donor (<span style="color:${report.donation_type === 'Paid' ? '#d9534f' : '#28a745'}">${report.donation_type}</span>)</p>
                        <p><strong>Mobile:</strong> ${report.phone || 'N/A'} | <strong>Blood:</strong> ${report.blood_group || 'N/A'}</p>
                        <p><strong>Status:</strong> <span class="status-badge ${report.status}">${report.status}</span></p>
                    </div>
                </div>
                <div class="report-actions">
                    <a href="/uploads/${report.filename}" target="_blank" class="btn-secondary btn-sm" style="text-decoration: none; line-height: 1.5;">View Doc</a>
                    <button class="btn-primary btn-sm" onclick="viewDetails('donor', ${JSON.stringify(report).replace(/"/g, '&quot;')})">View Details</button>
                </div>
            `;
                list.appendChild(card);
            });

            // We could update a badge here if we had one
            updateBadge('reportsList', pending);
        })
        .catch(error => {
            console.error('Error:', error);
            list.innerHTML = '<p>Error loading reports.</p>';
        });
}

function loadUsers(role, containerId) {
    const list = document.getElementById(containerId);
    const statusFilter = document.getElementById('verificationFilter').value;
    list.innerHTML = '<p>Loading...</p>';

    fetch(`/api/users?role=${role}`)
        .then(response => response.json())
        .then(users => {
            list.innerHTML = '';

            // Calculate pending for stats
            const pendingCount = users.filter(u => u.account_status === 'pending').length;
            if (role === 'hospital') dashboardStats.hospitals = pendingCount;
            if (role === 'blood_bank') dashboardStats.banks = pendingCount;
            updateGlobalStats();

            const filteredUsers = users.filter(u => {
                if (statusFilter === 'all') return true;
                // Map 'approved' filter to 'active' status in DB
                const targetStatus = statusFilter === 'approved' ? 'active' : statusFilter;
                return u.account_status === targetStatus;
            });

            if (filteredUsers.length === 0) {
                list.innerHTML = '<p>No records found.</p>';
                if (statusFilter === 'pending') {
                    updateBadge(containerId, 0);
                }
                return;
            }

            let pendingCountTab = 0;
            filteredUsers.forEach(user => {
                if (user.account_status === 'pending') pendingCountTab++;
                const card = document.createElement('div');
                card.className = 'report-card';
                card.innerHTML = `
                <div class="report-info">
                    <h4>${user.username}</h4>
                    <div class="report-meta">
                        <p><strong>Email:</strong> ${user.email}</p>
                         <p><strong>Phone:</strong> ${user.phone || 'N/A'}</p>
                        <p><strong>Status:</strong> <span class="status-badge ${user.account_status}">${user.account_status}</span></p>
                    </div>
                </div>
                <div class="report-actions">
                    <button class="btn-primary btn-sm" onclick="viewDetails('${role}', ${JSON.stringify(user).replace(/"/g, '&quot;')})">View Details</button>
                </div>
            `;
                list.appendChild(card);
            });
            updateBadge(containerId, pendingCountTab);
        })
        .catch(error => {
            console.error('Error:', error);
            list.innerHTML = '<p>Error loading data.</p>';
        });
}

function updateBadge(listId, count) {
    let badgeId = '';
    if (listId === 'reportsList') badgeId = 'donorsCount';
    if (listId === 'hospitalsList') badgeId = 'hospitalsCount';
    if (listId === 'banksList') badgeId = 'banksCount';

    const badge = document.getElementById(badgeId);
    if (badge) {
        badge.textContent = count > 0 ? count : '';
        badge.style.display = count > 0 ? 'inline-block' : 'none';
    }
}

// Modal Logic
const modal = document.getElementById('detailsModal');
const modalBody = document.getElementById('modalBody');
const modalFooter = document.getElementById('modalFooter');

function closeModal() {
    modal.style.display = "none";
}

window.onclick = function (event) {
    if (event.target == modal) {
        closeModal();
    }
}

function viewDetails(type, data) {
    let content = '';
    let actions = '';

    if (type === 'donor') {
        content = `
            <div class="detail-row"><span class="detail-label">Name:</span> <span class="detail-value">${data.donor_name}</span></div>
            <div class="detail-row"><span class="detail-label">Email:</span> <span class="detail-value">---</span></div> <!-- Email not in reports API yet, might need to fetch or ignore -->
            <div class="detail-row"><span class="detail-label">Phone:</span> <span class="detail-value">${data.phone}</span></div>
            <div class="detail-row"><span class="detail-label">Blood Group:</span> <span class="detail-value">${data.blood_group}</span></div>
            <div class="detail-row"><span class="detail-label">Donation Type:</span> <span class="detail-value">${data.donation_type}</span></div>
            <div class="detail-row"><span class="detail-label">Medical Cond.:</span> <span class="detail-value">${data.medical_conditions}</span></div>
            <div class="detail-row"><span class="detail-label">Proof Document:</span> <span class="detail-value">
                <a href="/uploads/${data.filename}" target="_blank" class="btn-sm btn-secondary">Open Document</a>
            </span></div>
        `;

        if (data.status === 'pending') {
            actions = `
                <button class="btn-danger" onclick="verifyReport(${data.id}, 'reject')">Reject</button>
                <button class="btn-primary" onclick="verifyReport(${data.id}, 'approve')">Approve</button>
            `;
        }
    } else {
        // Hospital or Bank
        content = `
            <div class="detail-row"><span class="detail-label">Name:</span> <span class="detail-value">${data.username}</span></div>
            <div class="detail-row"><span class="detail-label">Email:</span> <span class="detail-value">${data.email}</span></div>
            <div class="detail-row"><span class="detail-label">Phone:</span> <span class="detail-value">${data.phone}</span></div>
            <div class="detail-row"><span class="detail-label">Role:</span> <span class="detail-value">${data.role}</span></div>
            <div class="detail-row"><span class="detail-label">Status:</span> <span class="detail-value">${data.account_status}</span></div>
            
            <hr style="margin: 10px 0; border: 0; border-top: 1px solid #eee;">
            
            ${data.role === 'hospital' ? `
                <div class="detail-row"><span class="detail-label">Registration ID:</span> <span class="detail-value text-highlight">${data.registration_id || 'N/A'}</span></div>
                <div class="detail-row"><span class="detail-label">Type:</span> <span class="detail-value">${data.hospital_type || 'N/A'}</span></div>
                <div class="detail-row"><span class="detail-label">Beds:</span> <span class="detail-value">${data.capacity || 'N/A'}</span></div>
            ` : `
                <div class="detail-row"><span class="detail-label">License ID:</span> <span class="detail-value text-highlight">${data.license_id || 'N/A'}</span></div>
                <div class="detail-row"><span class="detail-label">Reg. Number:</span> <span class="detail-value">${data.registration_id || 'N/A'}</span></div>
                <div class="detail-row"><span class="detail-label">Capacity:</span> <span class="detail-value">${data.capacity || 'N/A'} units</span></div>
            `}
            
            <div class="detail-row"><span class="detail-label">Contact Person:</span> <span class="detail-value">${data.contact_person || 'N/A'}</span></div>
            <div class="detail-row"><span class="detail-label">Address:</span> <span class="detail-value">${data.address || 'N/A'}, ${data.city || ''}</span></div>
        `;

        if (data.account_status === 'pending') {
            actions = `
                <button class="btn-danger" onclick="verifyUser(${data.id}, 'reject')">Reject</button>
                <button class="btn-primary" onclick="verifyUser(${data.id}, 'approve')">Approve</button>
            `;
        }
    }

    modalBody.innerHTML = content;
    modalFooter.innerHTML = actions + `<button class="btn-secondary" onclick="closeModal()">Close</button>`;
    modal.style.display = "block";
}


function verifyUser(userId, action) {
    if (!confirm(`Are you sure you want to ${action} this user?`)) return;

    fetch(`/api/verify_user/${userId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: action })
    })
        .then(res => res.json())
        .then(data => {
            alert(data.message);
            closeModal();
            loadAllVerifications();
        })
        .catch(err => alert('Action failed'));
}

function verifyReport(reportId, action) {
    if (!confirm(`Are you sure you want to ${action} this report?`)) return;

    fetch(`/api/verify_report/${reportId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ action: action })
    })
        .then(response => response.json())
        .then(result => {
            alert(result.message);
            closeModal();
            loadReports();
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Action failed');
        });
}

function loadBloodRequests() {
    const list = document.getElementById('bloodRequestsList');
    list.innerHTML = '<p>Loading...</p>';

    fetch('/api/admin/requests')
        .then(response => response.json())
        .then(requests => {
            list.innerHTML = '';
            if (requests.length === 0) {
                list.innerHTML = '<p>No pending requests.</p>';
                return;
            }

            requests.forEach(req => {
                const card = document.createElement('div');
                card.className = 'report-card';
                card.innerHTML = `
                <div class="report-info">
                    <h4>Request from: ${req.hospital_name}</h4>
                    <div class="report-meta">
                        <p><strong>Patient:</strong> ${req.patient_name} (${req.blood_group})</p>
                        <p><strong>Units:</strong> ${req.units} | <strong>Priority:</strong> <span style="color: ${req.priority === 'emergency' ? 'red' : 'inherit'}">${req.priority.toUpperCase()}</span></p>
                        <p><strong>Bank:</strong> ${req.blood_bank || 'Any'}</p>
                        <p><strong>Reason:</strong> ${req.reason}</p>
                        <p>Requested: ${req.date}</p>
                    </div>
                </div>
                <div class="report-actions">
                    <button class="btn-primary btn-sm" onclick="verifyBloodRequest(${req.id}, 'approve')">Approve</button>
                    <button class="btn-danger btn-sm" onclick="verifyBloodRequest(${req.id}, 'reject')">Reject</button>
                </div>
            `;
                list.appendChild(card);
            });
        })
        .catch(error => {
            console.error('Error:', error);
            list.innerHTML = '<p>Error loading requests.</p>';
        });
}

function verifyBloodRequest(requestId, action) {
    if (!confirm(`Are you sure you want to ${action} this request?`)) return;

    fetch(`/api/admin/verify_request/${requestId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ action: action })
    })
        .then(response => response.json())
        .then(result => {
            alert(result.message);
            loadBloodRequests();
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Action failed');
        });
}
