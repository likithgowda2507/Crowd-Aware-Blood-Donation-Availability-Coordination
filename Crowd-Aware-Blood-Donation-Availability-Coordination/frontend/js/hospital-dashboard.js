// Hospital Dashboard JavaScript - Database Connected

document.addEventListener('DOMContentLoaded', function () {
    // Load User Profile
    loadUserProfile();

    // Load Dashboard Data
    const hospitalId = localStorage.getItem('user_id');
    if (hospitalId) {
        loadHospitalStats(hospitalId);
        loadActiveRequests(hospitalId);
        loadQuickStockCheck();
        loadAllRequests(hospitalId);
        loadBloodBanks();
        loadRequestHistory(hospitalId);
    }

    // Emergency Request Button
    const emergencyRequestBtn = document.getElementById('emergencyRequestBtn');
    const emergencyModal = document.getElementById('emergencyModal');

    if (emergencyRequestBtn && emergencyModal) {
        emergencyRequestBtn.addEventListener('click', function () {
            emergencyModal.style.display = 'flex';
        });
    }

    // Emergency Form Submission
    const emergencyForm = document.getElementById('emergencyForm');
    if (emergencyForm) {
        emergencyForm.addEventListener('submit', function (e) {
            e.preventDefault();

            const bloodGroup = document.getElementById('emergencyBloodGroup').value;
            const units = document.getElementById('emergencyUnits').value;
            const patientName = document.getElementById('emergencyPatientName').value;
            const reason = document.getElementById('emergencyReason').value;

            fetch('/api/blood-requests', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    hospital_id: hospitalId,
                    blood_group: bloodGroup,
                    units: units,
                    patient_name: patientName,
                    reason: reason,
                    priority: 'emergency'
                })
            })
                .then(res => res.json())
                .then(data => {
                    alert(data.message || 'Emergency request submitted!');
                    emergencyModal.style.display = 'none';
                    this.reset();
                    loadHospitalStats(hospitalId);
                    loadActiveRequests(hospitalId);
                    loadAllRequests(hospitalId);
                })
                .catch(err => alert('Error submitting request: ' + err));
        });
    }

    // Regular Blood Request Form
    const requestForm = document.getElementById('bloodRequestForm');
    if (requestForm) {
        requestForm.addEventListener('submit', function (e) {
            e.preventDefault();

            const bloodGroup = document.getElementById('bloodGroup').value;
            const units = document.getElementById('units').value;
            const patientName = document.getElementById('patientName').value;
            const reason = document.getElementById('reason').value;
            const priority = document.getElementById('priority').value;

            fetch('/api/blood-requests', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    hospital_id: hospitalId,
                    blood_group: bloodGroup,
                    units: units,
                    patient_name: patientName,
                    reason: reason,
                    priority: priority
                })
            })
                .then(res => res.json())
                .then(data => {
                    alert(data.message || 'Blood request submitted!');
                    this.reset();
                    loadHospitalStats(hospitalId);
                    loadActiveRequests(hospitalId);
                    loadAllRequests(hospitalId);
                })
                .catch(err => alert('Error submitting request: ' + err));
        });
    }

    // Quick Stock Check
    const checkStockBtn = document.getElementById('checkStockBtn');
    if (checkStockBtn) {
        checkStockBtn.addEventListener('click', function () {
            const bloodGroup = document.getElementById('quickBloodGroup').value;
            const stockResults = document.getElementById('stockResults');

            if (!bloodGroup) {
                alert('Please select a blood group');
                return;
            }

            fetch(`/api/stock-check?blood_group=${bloodGroup}`)
                .then(res => res.json())
                .then(data => {
                    stockResults.innerHTML = '';
                    if (data.length === 0) {
                        stockResults.innerHTML = '<p>No stock available for this blood group.</p>';
                        return;
                    }

                    data.forEach(bank => {
                        const div = document.createElement('div');
                        div.className = 'stock-result-item';
                        div.innerHTML = `
                            <h4>${bank.bank_name}</h4>
                            <p><strong>Available:</strong> ${bank.units} units</p>
                            <p><strong>Location:</strong> ${bank.city || 'N/A'}</p>
                            <button class="btn-primary btn-sm" onclick="requestFromBank(${bank.bank_id}, '${bloodGroup}')">Request</button>
                        `;
                        stockResults.appendChild(div);
                    });
                })
                .catch(err => {
                    stockResults.innerHTML = '<p>Error loading stock data.</p>';
                    console.error(err);
                });
        });
    }

    // --- Data Loading Functions ---

    function loadUserProfile() {
        const userId = localStorage.getItem('user_id');
        if (!userId) {
            window.location.href = 'login.html';
            return;
        }

        fetch(`/api/user/${userId}`)
            .then(res => res.json())
            .then(user => {
                const nameElements = document.querySelectorAll('.user-name');
                const locationElements = document.querySelectorAll('.user-blood');

                nameElements.forEach(el => el.textContent = user.username);
                locationElements.forEach(el => el.textContent = user.city || 'Hospital');
            })
            .catch(err => console.error('Error loading profile:', err));
    }

    function loadHospitalStats(hospitalId) {
        fetch(`/api/hospital/stats/${hospitalId}`)
            .then(res => res.json())
            .then(stats => {
                const statCards = document.querySelectorAll('.stat-card .stat-number');
                if (statCards[0]) statCards[0].textContent = stats.active_requests || 0;
                if (statCards[1]) statCards[1].textContent = stats.fulfilled_this_month || 0;
                if (statCards[2]) statCards[2].textContent = stats.units_received || 0;
                if (statCards[3]) statCards[3].textContent = (stats.avg_response_time || 0) + ' hrs';
            })
            .catch(err => console.error('Error loading stats:', err));
    }

    function loadActiveRequests(hospitalId) {
        const container = document.querySelector('.hospital-requests-list');
        if (!container) return;

        fetch(`/api/hospital/requests/${hospitalId}?status=active`)
            .then(res => res.json())
            .then(requests => {
                container.innerHTML = '';
                requests.forEach(req => {
                    const div = document.createElement('div');
                    div.className = `hospital-request-item ${req.priority}`;
                    div.innerHTML = `
                        <div class="request-status-indicator"></div>
                        <div class="request-details">
                            <div class="request-header-inline">
                                <h4>REQ-#${req.id}</h4>
                                <span class="priority-badge ${req.priority}">${req.priority}</span>
                            </div>
                            <p><strong>Blood Type:</strong> ${req.blood_group} | <strong>Units:</strong> ${req.units}</p>
                            <p><strong>Blood Bank:</strong> ${req.bank_name || 'Pending'}</p>
                            <p><strong>Status:</strong> ${req.status}</p>
                            <p><strong>Submitted:</strong> ${req.date}</p>
                        </div>
                        <button class="btn-secondary btn-sm" onclick="trackRequest(${req.id})">Track</button>
                    `;
                    container.appendChild(div);
                });

                if (requests.length === 0) {
                    container.innerHTML = '<p>No active requests.</p>';
                }
            })
            .catch(err => {
                console.error('Error loading active requests:', err);
                container.innerHTML = '<p>Error loading requests.</p>';
            });
    }

    function loadQuickStockCheck() {
        // Stock check is loaded on demand when user clicks the button
    }

    function loadAllRequests(hospitalId) {
        const container = document.getElementById('allRequestsContainer');
        if (!container) return;

        fetch(`/api/hospital/requests/${hospitalId}`)
            .then(res => res.json())
            .then(requests => {
                container.innerHTML = '';
                requests.forEach(req => {
                    const div = document.createElement('div');
                    div.className = `request-card ${req.priority}`;
                    div.innerHTML = `
                        <div class="request-header">
                            <div>
                                <h4>REQ-#${req.id}</h4>
                                <span class="priority-badge ${req.priority}">${req.priority}</span>
                            </div>
                            <span class="status-badge ${req.status}">${req.status}</span>
                        </div>
                        <div class="request-body">
                            <p><strong>Blood Type:</strong> ${req.blood_group}</p>
                            <p><strong>Units Required:</strong> ${req.units}</p>
                            <p><strong>Patient:</strong> ${req.patient_name}</p>
                            <p><strong>Reason:</strong> ${req.reason || 'N/A'}</p>
                            <p><strong>Blood Bank:</strong> ${req.bank_name || 'Pending'}</p>
                            <p><strong>Submitted:</strong> ${req.date}</p>
                        </div>
                        <div class="request-actions">
                            <button class="btn-secondary btn-sm">View Details</button>
                            ${req.status === 'pending' ? '<button class="btn-danger btn-sm" onclick="cancelRequest(' + req.id + ')">Cancel</button>' : ''}
                        </div>
                    `;
                    container.appendChild(div);
                });

                if (requests.length === 0) {
                    container.innerHTML = '<p>No requests found.</p>';
                }
            })
            .catch(err => {
                console.error('Error loading all requests:', err);
                container.innerHTML = '<p>Error loading requests.</p>';
            });
    }

    function loadBloodBanks() {
        const grid = document.getElementById('bloodBanksGrid');
        if (!grid) return;

        fetch('/api/banks')
            .then(res => res.json())
            .then(banks => {
                grid.innerHTML = '';
                banks.forEach(bank => {
                    const div = document.createElement('div');
                    div.className = 'blood-bank-card';
                    div.innerHTML = `
                        <div class="bank-header">
                            <h4>${bank.name}</h4>
                            <span class="status-badge available">Available</span>
                        </div>
                        <div class="bank-details">
                            <p><strong>Location:</strong> ${bank.city || 'N/A'}</p>
                            <p><strong>Contact:</strong> ${bank.phone || 'N/A'}</p>
                            <p><strong>Email:</strong> ${bank.email || 'N/A'}</p>
                        </div>
                        <div class="bank-actions">
                            <button class="btn-primary btn-sm" onclick="viewBankStock(${bank.id})">View Stock</button>
                            <button class="btn-secondary btn-sm" onclick="contactBank(${bank.id})">Contact</button>
                        </div>
                    `;
                    grid.appendChild(div);
                });

                if (banks.length === 0) {
                    grid.innerHTML = '<p>No blood banks found.</p>';
                }
            })
            .catch(err => {
                console.error('Error loading blood banks:', err);
                grid.innerHTML = '<p>Error loading blood banks.</p>';
            });
    }

    function loadRequestHistory(hospitalId) {
        const tbody = document.getElementById('historyTableBody');
        if (!tbody) return;

        fetch(`/api/hospital/requests/${hospitalId}?status=completed`)
            .then(res => res.json())
            .then(requests => {
                tbody.innerHTML = '';
                requests.forEach(req => {
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td>REQ-#${req.id}</td>
                        <td>${req.date}</td>
                        <td><span class="blood-type">${req.blood_group}</span></td>
                        <td>${req.units}</td>
                        <td>${req.bank_name || 'N/A'}</td>
                        <td><span class="status-badge ${req.status}">${req.status}</span></td>
                        <td><button class="btn-link" onclick="viewRequestDetails(${req.id})">View</button></td>
                    `;
                    tbody.appendChild(tr);
                });

                if (requests.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;">No history found.</td></tr>';
                }
            })
            .catch(err => {
                console.error('Error loading history:', err);
                tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;">Error loading history.</td></tr>';
            });
    }

    // Global helper functions
    window.trackRequest = function (reqId) {
        alert('Tracking request #' + reqId);
    };

    window.cancelRequest = function (reqId) {
        if (!confirm('Are you sure you want to cancel this request?')) return;

        fetch(`/api/blood-requests/${reqId}`, {
            method: 'DELETE'
        })
            .then(res => res.json())
            .then(data => {
                alert(data.message || 'Request cancelled');
                loadHospitalStats(hospitalId);
                loadActiveRequests(hospitalId);
                loadAllRequests(hospitalId);
            })
            .catch(err => alert('Error cancelling request: ' + err));
    };

    window.requestFromBank = function (bankId, bloodGroup) {
        alert(`Requesting ${bloodGroup} from bank #${bankId}`);
    };

    window.viewBankStock = function (bankId) {
        alert('Viewing stock for bank #' + bankId);
    };

    window.contactBank = function (bankId) {
        alert('Contacting bank #' + bankId);
    };

    window.viewRequestDetails = function (reqId) {
        alert('Viewing details for request #' + reqId);
    };
});