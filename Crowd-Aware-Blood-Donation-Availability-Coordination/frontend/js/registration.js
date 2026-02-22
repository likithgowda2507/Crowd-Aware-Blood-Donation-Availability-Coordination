// Registration Page JavaScript

document.addEventListener('DOMContentLoaded', function () {
    // Get role buttons and forms
    const roleButtons = document.querySelectorAll('.role-btn');
    const forms = document.querySelectorAll('.registration-form');

    // Get role from URL parameter if present
    const urlParams = new URLSearchParams(window.location.search);
    const roleParam = urlParams.get('role');

    // Set initial role
    if (roleParam) {
        const roleBtn = document.querySelector(`.role-btn[data-role="${roleParam}"]`);
        if (roleBtn) {
            switchRole(roleParam);
        }
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

        // Show corresponding form
        forms.forEach(form => form.classList.remove('active'));
        const activeForm = document.getElementById(`${role}Form`);
        if (activeForm) {
            activeForm.classList.add('active');
        }
    }

    // Form validation and submission
    forms.forEach(form => {
        form.addEventListener('submit', function (e) {
            e.preventDefault();

            // Basic validation
            if (!validateForm(this)) {
                return;
            }

            // Get form data
            const formData = new FormData(this);
            const data = Object.fromEntries(formData);

            // Validate password match
            if (data.password !== data.confirm_password) {
                alert('Passwords do not match!');
                return;
            }

            // Validate password match
            if (data.password !== data.confirm_password) {
                alert('Passwords do not match!');
                return;
            }

            // Send data to backend using FormData (handles files automatically)
            fetch('/api/register', {
                method: 'POST',
                body: formData // No Content-Type header needed for FormData, browser sets it with boundary
            })
                .then(response => response.json())
                .then(result => {
                    if (result.message.includes("successful")) {
                        alert('Registration successful! Please login to continue.');
                        window.location.href = 'login.html?role=' + (formData.get('role'));
                    } else {
                        alert('Registration failed: ' + result.message);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('An error occurred during registration.');
                });
        });
    });

    function validateForm(form) {
        const requiredFields = form.querySelectorAll('[required]');
        let isValid = true;

        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                field.style.borderColor = 'red';
                isValid = false;
            } else {
                field.style.borderColor = '';
            }
        });

        if (!isValid) {
            alert('Please fill in all required fields.');
        }

        return isValid;
    }

    // Donor age validation
    const donorAgeInput = document.getElementById('donor-age');
    if (donorAgeInput) {
        donorAgeInput.addEventListener('change', function () {
            const age = parseInt(this.value);
            if (age < 18 || age > 65) {
                alert('Donor age must be between 18 and 65 years.');
                this.value = '';
            }
        });
    }

    // Weight validation for donors
    const donorWeightInput = document.getElementById('donor-weight');
    if (donorWeightInput) {
        donorWeightInput.addEventListener('change', function () {
            const weight = parseInt(this.value);
            if (weight < 45) {
                alert('Minimum weight requirement is 45 kg for blood donation.');
                this.value = '';
            }
        });
    }

    // Phone number validation
    const phoneInputs = document.querySelectorAll('input[type="tel"]');
    phoneInputs.forEach(input => {
        input.addEventListener('input', function () {
            this.value = this.value.replace(/\D/g, '').slice(0, 10);
        });
    });

    // Pincode validation
    const pincodeInputs = document.querySelectorAll('input[name="pincode"]');
    pincodeInputs.forEach(input => {
        input.addEventListener('input', function () {
            this.value = this.value.replace(/\D/g, '').slice(0, 6);
        });
    });
});