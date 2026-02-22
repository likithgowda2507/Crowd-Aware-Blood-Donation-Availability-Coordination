// Login Page JavaScript

document.addEventListener('DOMContentLoaded', function () {
    // Get role buttons
    const roleButtons = document.querySelectorAll('.role-btn');
    const userRoleInput = document.getElementById('userRole');

    // Get role from URL parameter if present
    const urlParams = new URLSearchParams(window.location.search);
    const roleParam = urlParams.get('role');

    // Set initial role
    if (roleParam) {
        switchRole(roleParam);
    }

    // Role button click handlers
    roleButtons.forEach(button => {
        button.addEventListener('click', function () {
            const role = this.dataset.role;
            switchRole(role);
        });
    });

    function switchRole(role) {
        // Update active role button
        roleButtons.forEach(btn => btn.classList.remove('active'));
        const activeBtn = document.querySelector(`.role-btn[data-role="${role}"]`);
        if (activeBtn) {
            activeBtn.classList.add('active');
        }

        // Update hidden input
        if (userRoleInput) {
            userRoleInput.value = role;
        }
    }

    // Login form submission
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', function (e) {
            e.preventDefault();

            const formData = new FormData(this);
            const data = Object.fromEntries(formData);

            // Basic validation
            if (!data.email || !data.password) {
                alert('Please enter both email and password.');
                return;
            }

            // Email validation
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(data.email)) {
                alert('Please enter a valid email address.');
                return;
            }

            // Send credentials to backend
            console.log('Login attempt:', data);

            fetch('/api/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            })
                .then(response => response.json())
                .then(result => {
                    if (result.message === "Login successful") {
                        // Store user info
                        localStorage.setItem('user_id', result.user_id);
                        localStorage.setItem('username', result.username);
                        localStorage.setItem('role', result.role);

                        alert('Login successful! Redirecting to dashboard...');
                        window.location.href = result.redirect_url;
                    } else if (result.message === "Account pending approval") {
                        alert('Your account is pending verification. Please wait for the admin to approve your uploaded report.');
                    } else {
                        alert('Login failed: ' + result.message);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('An error occurred during login.');
                });
        });
    }

    // Show/hide password (optional enhancement)
    const passwordInput = document.getElementById('password');
    if (passwordInput) {
        passwordInput.addEventListener('dblclick', function () {
            if (this.type === 'password') {
                this.type = 'text';
                setTimeout(() => {
                    this.type = 'password';
                }, 1000);
            }
        });
    }
});