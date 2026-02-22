// Donor Dashboard JavaScript

document.addEventListener('DOMContentLoaded', function () {
    const userId = localStorage.getItem('user_id');
    const userRole = localStorage.getItem('role');

    if (!userId || userRole !== 'donor') {
        window.location.href = 'login.html';
        return;
    }

    // Initialize Dashboard
    loadUserProfile(userId);
    loadDonorStats(userId);
    loadCampaigns(); // Loads for both dashboard widget and camps section
    loadAppointments(userId);
    loadNotifications(userId);

    // --- Data Loading Functions ---

    function loadNotifications(id) {
        fetch(`/api/notifications/${id}`)
            .then(res => res.json())
            .then(notifs => {
                const list = document.getElementById('notificationsList');
                if (!list) return;

                if (notifs.length === 0) {
                    list.innerHTML = '<p class="no-data">No notifications.</p>';
                } else {
                    list.innerHTML = notifs.map(n => `
                        <div class="notification-card ${n.type} ${n.is_read ? '' : 'unread'}">
                            <div class="notification-icon ${n.type}">
                                ${getNotificationIcon(n.type)}
                            </div>
                            <div class="notification-content">
                                <h4>${n.type.charAt(0).toUpperCase() + n.type.slice(1)}: ${n.message}</h4>
                                <span class="notification-time">${n.time_ago}</span>
                                ${n.type === 'urgent' ? `
                                <div class="notification-actions">
                                    <button class="btn-primary btn-sm">I Can Donate</button>
                                    <button class="btn-secondary btn-sm">Not Available</button>
                                </div>` : ''}
                            </div>
                        </div>
                    `).join('');
                }
            })
            .catch(err => console.error('Error loading notifications:', err));
    }

    function getNotificationIcon(type) {
        switch (type) {
            case 'urgent': return '🚨';
            case 'success': return '✓';
            case 'info': return 'ℹ️';
            case 'warning': return '⚠️';
            default: return '📢';
        }
    }

    function loadUserProfile(id) {
        fetch(`/api/user/${id}`)
            .then(res => res.json())
            .then(user => {
                // Update Sidebar and Header
                document.querySelectorAll('.user-name').forEach(el => el.textContent = user.username);
                document.querySelector('.user-role').textContent = user.role.charAt(0).toUpperCase() + user.role.slice(1);

                // Update Profile Form Fields
                const inputs = document.querySelectorAll('#profileForm input, #profileForm textarea');
                inputs.forEach(input => {
                    const field = input.dataset.field || input.name; // Use data-field or name
                    // Map known fields
                    if (field === 'username') input.value = user.username;
                    if (field === 'email') input.value = user.email;
                    if (field === 'phone') input.value = user.phone || '';
                    if (field === 'address') input.value = user.address || '';
                    if (field === 'city' && input.name === 'city') input.value = user.city || '';

                    // Specific fields if they exist in HTML (some were static in original)
                    if (input.type === 'text' && input.value === 'Male') input.value = 'Male'; // Placeholder for gender if not in DB
                    if (input.type === 'text' && input.value === 'O+') input.value = user.blood_group || 'Unknown';
                });
            })
            .catch(err => console.error('Error loading profile:', err));
    }

    function loadDonorStats(id) {
        fetch(`/api/donor/stats/${id}`)
            .then(res => res.json())
            .then(stats => {
                const statsGrid = document.getElementById('statsGrid');
                if (statsGrid) {
                    statsGrid.innerHTML = `
                        <div class="stat-card">
                            <div class="stat-icon">💉</div>
                            <div class="stat-details">
                                <h3>Total Donations</h3>
                                <p class="stat-number">${stats.total_donations}</p>
                            </div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-icon">❤️</div>
                            <div class="stat-details">
                                <h3>Lives Saved</h3>
                                <p class="stat-number">${stats.lives_saved}</p>
                            </div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-icon">📅</div>
                            <div class="stat-details">
                                <h3>Next Eligible</h3>
                                <p class="stat-number">${stats.days_remaining > 0 ? stats.days_remaining + ' days' : 'Eligible Now'}</p>
                            </div>
                        </div>
                        <div class="stat-card">
                            <div class="stat-icon">🏆</div>
                            <div class="stat-details">
                                <h3>Achievement Level</h3>
                                <p class="stat-number">${stats.achievement_level}</p>
                            </div>
                        </div>
                    `;
                }

                // Update Eligibility Widget
                const eligibilityWidget = document.getElementById('eligibilityWidget');
                if (eligibilityWidget) {
                    const isEligible = stats.days_remaining === 0;
                    eligibilityWidget.innerHTML = `
                        <div class="eligibility-card ${isEligible ? 'eligible' : 'ineligible'}">
                            <div class="status-icon">${isEligible ? '✓' : '⏳'}</div>
                            <div class="status-details">
                                <h4>${isEligible ? 'Currently Eligible' : 'Wait Period'}</h4>
                                <p>${isEligible ? 'You can donate blood now' : `You can donate in ${stats.days_remaining} days`}</p>
                                ${isEligible ? '<a href="#book-slot" class="btn-primary" onclick="document.querySelector(\'[data-section=book-slot]\').click()">Book Donation Slot</a>' : ''}
                            </div>
                        </div>
                    `;
                }
            })
            .catch(err => console.error('Error loading stats:', err));
    }

    function loadCampaigns() {
        fetch('/api/campaigns')
            .then(res => res.json())
            .then(camps => {
                // 1. Dashboard Widget List
                const dashboardList = document.getElementById('dashboardCampList');
                if (dashboardList) {
                    if (camps.length === 0) {
                        dashboardList.innerHTML = '<p>No upcoming camps found.</p>';
                    } else {
                        dashboardList.innerHTML = camps.slice(0, 3).map(camp => `
                            <div class="camp-item">
                                <div class="camp-date">
                                    <span class="day">${new Date(camp.date).getDate()}</span>
                                    <span class="month">${new Date(camp.date).toLocaleString('default', { month: 'short' })}</span>
                                </div>
                                <div class="camp-details">
                                    <h4>${camp.name}</h4>
                                    <p>📍 ${camp.location}</p>
                                    <p>⏰ ${camp.start_time} - ${camp.end_time}</p>
                                </div>
                                <button class="btn-secondary btn-sm" onclick="preselectCamp('${camp.id}', '${camp.name}', '${camp.date}', '${camp.start_time}')">Book Slot</button>
                            </div>
                        `).join('');
                    }
                }

                // 2. All Camps Grid
                const allCampsGrid = document.getElementById('allCampsGrid');
                if (allCampsGrid) {
                    if (camps.length === 0) {
                        allCampsGrid.innerHTML = '<p>No camps available at the moment.</p>';
                    } else {
                        allCampsGrid.innerHTML = camps.map(camp => `
                            <div class="camp-card">
                                <div class="camp-card-header">
                                    <h3>${camp.name}</h3>
                                    <span class="camp-status available">Available</span>
                                </div>
                                <div class="camp-card-body">
                                    <p><strong>📍 Location:</strong> ${camp.location}</p>
                                    <p><strong>📅 Date:</strong> ${camp.date}</p>
                                    <p><strong>⏰ Time:</strong> ${camp.start_time} - ${camp.end_time}</p>
                                </div>
                                <div class="camp-card-footer">
                                    <button class="btn-primary btn-block" onclick="preselectCamp('${camp.id}', '${camp.name}', '${camp.date}', '${camp.start_time}')">Book Slot</button>
                                </div>
                            </div>
                        `).join('');
                    }
                }

                // 3. Booking Form Selection
                const bookingList = document.getElementById('bookingCampList');
                if (bookingList) {
                    if (camps.length === 0) {
                        bookingList.innerHTML = '<p>No camps available for booking.</p>';
                    } else {
                        bookingList.innerHTML = camps.map(camp => `
                            <label class="camp-option">
                                <input type="radio" name="camp" value="${camp.id}" data-name="${camp.name}" data-date="${camp.date}" data-time="${camp.start_time}" required>
                                <div class="camp-option-content">
                                    <h4>${camp.name}</h4>
                                    <p>${camp.location}</p>
                                    <p>${camp.date} | ${camp.start_time} - ${camp.end_time}</p>
                                </div>
                            </label>
                        `).join('');
                    }
                }
            })
            .catch(err => console.error('Error loading camps:', err));
    }

    function loadAppointments(id) {
        fetch(`/api/appointments/${id}`)
            .then(res => res.json())
            .then(appts => {
                const upcomingList = document.getElementById('upcomingAppointmentsList');
                const pastList = document.getElementById('pastAppointmentsList');

                const now = new Date();
                const upcoming = appts.filter(a => new Date(a.date) >= now);
                const past = appts.filter(a => new Date(a.date) < now);

                if (upcomingList) {
                    if (upcoming.length === 0) {
                        upcomingList.innerHTML = '<p class="no-data">No upcoming appointments.</p>';
                    } else {
                        upcomingList.innerHTML = upcoming.map(a => `
                            <div class="appointment-card">
                                <div class="appointment-header">
                                    <h3>${a.title}</h3>
                                    <span class="appointment-status ${a.status.toLowerCase()}">${a.status}</span>
                                </div>
                                <div class="appointment-body">
                                    <p><strong>📅 Date:</strong> ${a.date}</p>
                                    <p><strong>⏰ Time:</strong> ${a.time}</p>
                                    <p><strong>📍 Location:</strong> ${a.location}</p>
                                    <p><strong>🆔 Ref:</strong> #${a.id}</p>
                                </div>
                                <div class="appointment-footer">
                                    <button class="btn-danger btn-sm">Cancel</button>
                                </div>
                            </div>
                        `).join('');
                    }
                }

                if (pastList) {
                    if (past.length === 0) {
                        pastList.innerHTML = '<p class="no-data">No past appointments.</p>';
                    } else {
                        pastList.innerHTML = past.map(a => `
                            <div class="appointment-card">
                                <div class="appointment-header">
                                    <h3>${a.title}</h3>
                                    <span class="appointment-status completed">Completed</span>
                                </div>
                                <div class="appointment-body">
                                    <p><strong>📅 Date:</strong> ${a.date}</p>
                                    <p><strong>⏰ Time:</strong> ${a.time}</p>
                                    <p><strong>📍 Location:</strong> ${a.location}</p>
                                </div>
                            </div>
                        `).join('');
                    }
                }
            })
            .catch(err => console.error('Error loading appointments:', err));
    }

    // --- Booking Logic ---
    window.preselectCamp = function (id, name, date, time) {
        // Switch to Book Slot tab
        const bookSlotNav = document.querySelector('[data-section="book-slot"]');
        if (bookSlotNav) bookSlotNav.click();

        // Wait a bit for render then select
        setTimeout(() => {
            const radio = document.querySelector(`input[name="camp"][value="${id}"]`);
            if (radio) {
                radio.checked = true;
                // Update specific summary fields if needed or just let the nextStep handle it
            }
        }, 100);
    };

    const bookingForm = document.getElementById('bookingForm');
    if (bookingForm) {

        // Step Navigation (Simplified from original)
        window.nextStep = function (step) {
            // Logic to move between steps
            document.querySelectorAll('.form-step').forEach(s => s.classList.remove('active'));
            document.querySelector(`.form-step[data-step="${step}"]`).classList.add('active');

            // Populating Summary on Step 3
            if (step === 3) {
                const selectedCamp = document.querySelector('input[name="camp"]:checked');
                const selectedTime = document.querySelector('input[name="time"]:checked');

                if (selectedCamp) {
                    document.getElementById('summarycamp').textContent = selectedCamp.dataset.name;
                    document.getElementById('summaryDate').textContent = selectedCamp.dataset.date;
                    document.getElementById('summaryLocation').textContent = "See Camp Details";
                }
                if (selectedTime) {
                    document.getElementById('summaryTime').textContent = selectedTime.parentElement.querySelector('span').textContent;
                }
            }
        };

        window.prevStep = function (step) {
            document.querySelectorAll('.form-step').forEach(s => s.classList.remove('active'));
            document.querySelector(`.form-step[data-step="${step}"]`).classList.add('active');
        };

        bookingForm.addEventListener('submit', function (e) {
            e.preventDefault();

            const selectedCamp = document.querySelector('input[name="camp"]:checked');
            const selectedTime = document.querySelector('input[name="time"]:checked');

            if (!selectedCamp || !selectedTime) {
                alert("Please select a camp and time slot.");
                return;
            }

            const bookingData = {
                donor_id: userId,
                camp_id: selectedCamp.value,
                date: selectedCamp.dataset.date,
                time_slot: selectedTime.value
            };

            fetch('/api/appointments', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(bookingData)
            })
                .then(res => res.json())
                .then(data => {
                    if (data.id) {
                        alert('Appointment booked successfully!');
                        bookingForm.reset();
                        window.location.reload(); // Reload to see new appointment and stats
                    } else {
                        alert('Booking failed: ' + data.message);
                    }
                })
                .catch(err => console.error('Booking error:', err));
        });
    }

    // --- Profile Editing (Preserved) ---
    const editProfileBtn = document.getElementById('editProfileBtn');
    const cancelEditBtn = document.getElementById('cancelEditBtn');
    const profileForm = document.getElementById('profileForm');
    const formActions = document.querySelector('.form-actions');

    if (editProfileBtn) {
        editProfileBtn.addEventListener('click', function () {
            const inputs = profileForm.querySelectorAll('input, textarea, select');
            inputs.forEach(input => input.disabled = false);
            if (formActions) formActions.style.display = 'flex';
            this.style.display = 'none';
        });
    }

    if (cancelEditBtn) {
        cancelEditBtn.addEventListener('click', function () {
            const inputs = profileForm.querySelectorAll('input, textarea, select');
            inputs.forEach(input => input.disabled = true);
            if (formActions) formActions.style.display = 'none';
            if (editProfileBtn) editProfileBtn.style.display = 'inline-block';
            profileForm.reset();
            loadUserProfile(userId); // Reload original data
        });
    }

    // Report Upload (Preserved)
    const uploadReportForm = document.getElementById('uploadReportForm');
    if (uploadReportForm) {
        uploadReportForm.addEventListener('submit', function (e) {
            e.preventDefault();
            const fileInput = document.getElementById('reportFile');
            const file = fileInput.files[0];

            if (!file) return alert('Please select a file');

            const formData = new FormData();
            formData.append('report', file);
            formData.append('donor_id', userId);

            fetch('/api/upload_report', {
                method: 'POST',
                body: formData
            })
                .then(res => res.json())
                .then(result => {
                    alert(result.message);
                    if (result.message.includes('success')) uploadReportForm.reset();
                })
                .catch(err => console.error('Error:', err));
        });
    }
});