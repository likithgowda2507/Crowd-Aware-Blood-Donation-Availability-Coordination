// Blood Bank Dashboard JavaScript - Database Connected

document.addEventListener('DOMContentLoaded', function () {
    // Load User Profile
    loadUserProfile();

    // Load Dashboard Data
    const bankId = localStorage.getItem('user_id');
    if (bankId) {
        loadBankStats(bankId);
        loadBankInventory(bankId); // Overview Widget
        loadDetailedInventory(bankId); // Inventory Tab
        loadCamps(bankId);
        loadBankRequests(bankId);
        loadBankDonations(bankId);
        loadNetwork(bankId);
    }

    // Wiring up Add Stock Button
    const addStockBtn = document.getElementById('addStockBtn');
    const addStockModal = document.getElementById('addStockModal');
    if (addStockBtn && addStockModal) {
        addStockBtn.addEventListener('click', () => {
            addStockModal.style.display = 'flex';
        });
    }

    const addStockForm = document.getElementById('addStockForm');
    if (addStockForm) {
        addStockForm.addEventListener('submit', function (e) {
            e.preventDefault();
            const group = document.getElementById('stockGroup').value;
            const units = document.getElementById('stockUnits').value;
            const expiry = document.getElementById('stockExpiry').value;

            fetch('/api/inventory/update', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    bank_id: bankId,
                    blood_group: group,
                    units: units,
                    expiry_date: expiry
                })
            })
                .then(res => res.json())
                .then(data => {
                    if (data.message.includes('successfully')) {
                        alert('Stock updated!');
                        addStockModal.style.display = 'none';
                        loadBankStats(bankId);
                        loadBankInventory(bankId);
                        loadDetailedInventory(bankId);
                    } else {
                        alert('Error: ' + data.message);
                    }
                });
        });
    }

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
                const locationElements = document.querySelectorAll('.user-blood, .user-location');

                nameElements.forEach(el => el.textContent = user.username);
                locationElements.forEach(el => el.textContent = user.city || 'Blood Bank');

                const welcomeMsg = document.getElementById('welcomeMessage');
                if (welcomeMsg) welcomeMsg.textContent = `Welcome, ${user.username}`;
            })
            .catch(err => console.error('Error loading profile:', err));
    }

    // Create Camp Logic
    const createCampBtn = document.getElementById('createCampBtn');
    const createCampForm = document.getElementById('createCampForm'); // Modal container

    if (createCampBtn && createCampForm) {
        createCampBtn.addEventListener('click', function () {
            createCampForm.style.display = 'flex';
        });
    }

    const campFormEl = createCampForm ? createCampForm.querySelector('form') : null;
    if (campFormEl) {
        campFormEl.addEventListener('submit', function (e) {
            e.preventDefault();

            const name = document.getElementById('campName').value;
            const date = document.getElementById('campDate').value;
            const start = document.getElementById('campStart').value;
            const end = document.getElementById('campEnd').value;
            const loc = document.getElementById('campLocation').value;
            const target = document.getElementById('campTarget').value;

            fetch('/api/campaigns', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    organizer_id: bankId,
                    name: name,
                    date: date,
                    start_time: start,
                    end_time: end,
                    location: loc,
                    target_blood_groups: target
                })
            })
                .then(res => res.json())
                .then(data => {
                    alert(data.message);
                    createCampForm.style.display = 'none';
                    loadCamps(bankId);
                });
        });
    }

    // --- Data Loading Functions ---

    function loadDetailedInventory(bankId) {
        const tbody = document.getElementById('inventoryTableBody');
        if (!tbody) return;

        fetch(`/api/bank/inventory/details/${bankId}`)
            .then(res => res.json())
            .then(data => {
                tbody.innerHTML = '';
                data.forEach(item => {
                    const tr = document.createElement('tr');

                    tr.innerHTML = `
                        <td>${item.bag_id}</td>
                        <td><span class="blood-type">${item.blood_group}</span></td>
                        <td>${item.volume}</td>
                        <td>${item.collection_date}</td>
                        <td>${item.expiry_date}</td>
                        <td><span class="status-badge ${item.status_class}">${item.status}</span></td>
                        <td><button class="btn-link" onclick="alert('QR Code: ${item.bag_id}')">View QR</button></td>
                        <td>
                            <button class="btn-icon" title="Edit" onclick="alert('Edit ${item.bag_id}')">✏️</button>
                            <button class="btn-icon" title="Reserve" onclick="alert('Reserve ${item.bag_id}')">📌</button>
                        </td>
                    `;
                    tbody.appendChild(tr);
                });

                if (data.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="8" style="text-align:center;">No inventory records found.</td></tr>';
                }
            })
            .catch(err => {
                console.error('Error loading detailed inventory:', err);
                tbody.innerHTML = '<tr><td colspan="8" style="text-align:center;">Error loading inventory.</td></tr>';
            });
    }

    // Global storage for camps to avoid passing complex objects in HTML
    window.campsMap = {};

    function loadCamps(bankId) {
        const container = document.querySelector('.camps-grid');
        if (!container) return;

        fetch('/api/campaigns')
            .then(res => res.json())
            .then(camps => {
                container.innerHTML = '';

                // Reset map
                window.campsMap = {};

                camps.forEach(camp => {
                    // Store in global map
                    window.campsMap[camp.id] = camp;

                    const div = document.createElement('div');
                    div.className = 'camp-management-card';
                    div.innerHTML = `
                        <div class="camp-card-header">
                            <h4>${camp.name}</h4>
                            <span class="camp-badge ${camp.status === 'cancelled' ? 'cancelled' : 'active'}">${camp.status || 'Scheduled'}</span>
                        </div>
                        <div class="camp-card-body">
                            <p><strong>Date:</strong> ${camp.date}</p>
                            <p><strong>Time:</strong> ${camp.start_time || '--'} - ${camp.end_time || '--'}</p>
                            <p><strong>Location:</strong> ${camp.location}</p>
                        </div>
                        <div class="camp-card-footer">
                            <button class="btn-secondary btn-sm" onclick='openManageSlots(${camp.id})'>Manage Slots</button>
                            <button class="btn-secondary btn-sm" onclick='openEditCamp(${camp.id})'>Edit Camp</button>
                            <button class="btn-danger btn-sm" onclick="cancelCamp(${camp.id})">Cancel Camp</button>
                        </div>
                    `;
                    container.appendChild(div);
                });

                if (camps.length === 0) container.innerHTML = '<p>No active camps.</p>';
            })
            .catch(err => {
                console.error('Error loading camps:', err);
                container.innerHTML = '<p>Error loading camps.</p>';
            });
    }

    // --- Global Handlers for Camp Management ---

    window.openEditCamp = function (campId) {
        const camp = window.campsMap[campId];
        if (!camp) {
            console.error("Camp data not found for ID:", campId);
            return;
        }

        document.getElementById('editCampId').value = camp.id;
        document.getElementById('editCampName').value = camp.name;
        document.getElementById('editCampDate').value = camp.date;
        document.getElementById('editCampStart').value = camp.start_time;
        document.getElementById('editCampEnd').value = camp.end_time;
        document.getElementById('editCampLocation').value = camp.location;

        document.getElementById('editCampModal').style.display = 'flex';
    };

    const editCampForm = document.getElementById('editCampForm');
    if (editCampForm) {
        editCampForm.addEventListener('submit', function (e) {
            e.preventDefault();
            const campId = document.getElementById('editCampId').value;

            fetch(`/api/camps/${campId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name: document.getElementById('editCampName').value,
                    date: document.getElementById('editCampDate').value,
                    start_time: document.getElementById('editCampStart').value,
                    end_time: document.getElementById('editCampEnd').value,
                    location: document.getElementById('editCampLocation').value
                })
            })
                .then(res => res.json())
                .then(data => {
                    alert(data.message);
                    document.getElementById('editCampModal').style.display = 'none';
                    loadCamps(localStorage.getItem('user_id'));
                });
        });
    }

    window.cancelCamp = function (campId) {
        if (!confirm('Are you sure you want to cancel this camp? This cannot be undone.')) return;

        fetch(`/api/camps/${campId}`, {
            method: 'DELETE'
        })
            .then(res => res.json())
            .then(data => {
                alert(data.message);
                loadCamps(localStorage.getItem('user_id'));
            });
    };

    window.openManageSlots = function (campId) {
        const modal = document.getElementById('manageSlotsModal');
        const tbody = document.getElementById('slotsTableBody');
        tbody.innerHTML = '<tr><td colspan="3">Loading slots...</td></tr>';
        modal.style.display = 'flex';

        fetch(`/api/camps/${campId}/slots`)
            .then(res => res.json())
            .then(slots => {
                tbody.innerHTML = '';
                if (slots.length === 0) {
                    tbody.innerHTML = '<tr><td colspan="3">No appointments booked yet.</td></tr>';
                    return;
                }

                slots.forEach(slot => {
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td>${slot.donor_name}</td>
                        <td>${slot.time}</td>
                        <td><span class="status-badge ${slot.status === 'confirmed' ? 'status-good' : 'status-low'}">${slot.status}</span></td>
                    `;
                    tbody.appendChild(tr);
                });
            });
    };

    function loadBankRequests(bankId) {
        const container = document.querySelector('.requests-list');
        if (!container) return;

        fetch(`/api/bank/requests/${bankId}`)
            .then(res => res.json())
            .then(requests => {
                container.innerHTML = '';
                requests.forEach(req => {
                    if (req.status !== 'pending') return;

                    const div = document.createElement('div');
                    div.className = `request-card ${req.priority === 'emergency' ? 'emergency' : 'high'}`;
                    div.innerHTML = `
                        <div class="request-header">
                            <div>
                                <h4>${req.hospital_name}</h4>
                                <span class="request-id">REQ-#${req.id}</span>
                            </div>
                            <span class="priority-badge ${req.priority}">${req.priority}</span>
                        </div>
                        <div class="request-body">
                             <div class="request-details">
                                <p><strong>Blood Type:</strong> ${req.blood_group}</p>
                                <p><strong>Units Required:</strong> ${req.units}</p>
                                <p><strong>Patient ID:</strong> ${req.patient_name}</p>
                                <p><strong>Requested:</strong> ${req.date}</p>
                            </div>
                        </div>
                        <div class="request-actions">
                            <button class="btn-primary" onclick="handleRequestAction(${req.id}, 'approve', ${bankId})">Approve Request</button>
                            <button class="btn-secondary">Contact Hospital</button>
                            <button class="btn-danger" onclick="handleRequestAction(${req.id}, 'reject', ${bankId})">Reject</button>
                        </div>
                    `;
                    container.appendChild(div);
                });

                if (container.children.length === 0) container.innerHTML = '<p>No pending requests.</p>';
            })
            .catch(err => {
                console.error('Error loading requests:', err);
                container.innerHTML = '<p>Error loading requests.</p>';
            });
    }

    window.handleRequestAction = function (reqId, action, bankId) {
        if (!confirm(`Are you sure you want to ${action} this request?`)) return;

        fetch(`/api/bank/request/${reqId}/action`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action: action, bank_id: bankId })
        })
            .then(res => res.json())
            .then(data => {
                alert(data.message);
                loadBankRequests(bankId);
                loadBankStats(bankId); // Update pending count
                loadBankInventory(bankId); // Update stock
            })
            .catch(err => alert('Action failed: ' + err));
    };

    function loadBankDonations(bankId) {
        const tbody = document.querySelector('#donations .data-table tbody');
        if (!tbody) return;

        fetch(`/api/bank/donations/${bankId}`)
            .then(res => res.json())
            .then(donations => {
                tbody.innerHTML = '';
                donations.forEach(d => {
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td>${d.date}</td>
                        <td>${d.donor_name}</td>
                        <td><span class="blood-type">${d.blood_group}</span></td>
                        <td>450 ml</td>
                        <td>BB-2026-${String(d.id).padStart(4, '0')}</td>
                        <td>${d.type}</td>
                        <td><button class="btn-link">Generate</button></td>
                    `;
                    tbody.appendChild(tr);
                });
                if (donations.length === 0) tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;">No donations found.</td></tr>';
            })
            .catch(err => {
                console.error('Error loading donations:', err);
                tbody.innerHTML = '<tr><td colspan="7" style="text-align:center;">Error loading donations.</td></tr>';
            });
    }

    function loadNetwork(bankId) {
        const grid = document.querySelector('.network-grid');
        if (!grid) return;

        fetch('/api/banks')
            .then(res => res.json())
            .then(banks => {
                grid.innerHTML = '';
                banks.forEach(bank => {
                    if (bank.id == bankId) return; // Skip self

                    const div = document.createElement('div');
                    div.className = 'network-card connected';
                    div.innerHTML = `
                        <div class="network-header">
                            <h4>${bank.name}</h4>
                            <span class="connection-badge">Connected</span>
                        </div>
                        <div class="network-body">
                            <p><strong>Location:</strong> ${bank.city || 'N/A'}</p>
                            <p><strong>Contact:</strong> ${bank.phone || 'N/A'}</p>
                        </div>
                        <div class="network-actions">
                            <button class="btn-secondary btn-sm" onclick="alert('Request sent to ${bank.name}')">Request Blood</button>
                            <button class="btn-secondary btn-sm">View Full Stock</button>
                        </div>
                    `;
                    grid.appendChild(div);
                });

                if (grid.children.length === 0) grid.innerHTML = '<p>No other blood banks found.</p>';
            })
            .catch(err => {
                console.error('Error loading network:', err);
                grid.innerHTML = '<p>Error loading network.</p>';
            });
    }

    function loadBankStats(bankId) {
        fetch(`/api/bank/stats/${bankId}`)
            .then(res => res.json())
            .then(stats => {
                // Update stat cards
                const statCards = document.querySelectorAll('.stat-card .stat-number');
                if (statCards[0]) statCards[0].textContent = stats.total_units.toLocaleString();
                if (statCards[1]) statCards[1].textContent = stats.todays_collections;
                if (statCards[2]) statCards[2].textContent = stats.pending_requests;
                if (statCards[3]) statCards[3].textContent = stats.expiring_soon;

                // Update urgent label
                const urgentLabel = document.querySelector('.stat-change.urgent');
                if (urgentLabel && stats.pending_requests > 0) {
                    urgentLabel.textContent = `${stats.pending_requests} urgent`;
                }
            })
            .catch(err => console.error('Error loading stats:', err));
    }

    function loadBankInventory(bankId) {
        const grid = document.querySelector('.blood-groups-grid');
        if (!grid) return;

        grid.innerHTML = '<p>Loading...</p>';

        fetch(`/api/bank/inventory/${bankId}`)
            .then(res => res.json())
            .then(data => {
                grid.innerHTML = '';
                const bloodGroups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'];

                bloodGroups.forEach(bg => {
                    const units = data[bg] || 0;
                    let statusClass = 'status-good';
                    let statusLabel = 'Good Stock';
                    let width = '80%';

                    if (units < 10) {
                        statusClass = 'status-critical';
                        statusLabel = 'Critical';
                        width = '10%';
                    } else if (units < 30) {
                        statusClass = 'status-low';
                        statusLabel = 'Low Stock';
                        width = '35%';
                    } else {
                        width = Math.min(100, (units / 100) * 100) + '%';
                    }

                    const card = document.createElement('div');
                    card.className = `blood-group-card ${statusClass}`;
                    card.innerHTML = `
                        <h4>${bg}</h4>
                        <p class="units">${units} units</p>
                        <div class="stock-bar">
                            <div class="stock-fill" style="width: ${width}"></div>
                        </div>
                        <span class="status-label">${statusLabel}</span>
                    `;
                    grid.appendChild(card);
                });
            })
            .catch(err => {
                console.error('Error loading inventory:', err);
                grid.innerHTML = '<p>Error loading inventory data.</p>';
            });
    }
});