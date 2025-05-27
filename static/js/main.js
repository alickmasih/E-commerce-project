// Form validation
document.addEventListener('DOMContentLoaded', function() {
    // Credit card validation
    const ccNumber = document.getElementById('cc-number');
    if (ccNumber) {
        ccNumber.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length > 16) value = value.slice(0, 16);
            e.target.value = value;
        });
    }

    // CVV validation
    const ccCvv = document.getElementById('cc-cvv');
    if (ccCvv) {
        ccCvv.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length > 3) value = value.slice(0, 3);
            e.target.value = value;
        });
    }

    // Expiration date validation
    const ccExpiration = document.getElementById('cc-expiration');
    if (ccExpiration) {
        ccExpiration.addEventListener('input', function(e) {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length >= 2) {
                value = value.slice(0, 2) + '/' + value.slice(2, 4);
            }
            e.target.value = value;
        });
    }

    // Quantity input validation
    const quantityInputs = document.querySelectorAll('input[name="quantity"]');
    quantityInputs.forEach(input => {
        input.addEventListener('change', function(e) {
            const value = parseInt(e.target.value);
            const max = parseInt(e.target.max);
            if (value < 1) e.target.value = 1;
            if (value > max) e.target.value = max;
        });
    });

    // Login password toggle
    const togglePassword = document.getElementById('togglePassword');
    const password = document.getElementById('password');
    
    if (togglePassword && password) {
        togglePassword.addEventListener('click', function() {
            const type = password.getAttribute('type') === 'password' ? 'text' : 'password';
            password.setAttribute('type', type);
            this.querySelector('i').classList.toggle('fa-eye');
            this.querySelector('i').classList.toggle('fa-eye-slash');
        });
    }

    // Signup password toggle
    const toggleSignupPassword = document.getElementById('toggleSignupPassword');
    const signupPassword = document.getElementById('signup-password');
    
    if (toggleSignupPassword && signupPassword) {
        toggleSignupPassword.addEventListener('click', function() {
            const type = signupPassword.getAttribute('type') === 'password' ? 'text' : 'password';
            signupPassword.setAttribute('type', type);
            this.querySelector('i').classList.toggle('fa-eye');
            this.querySelector('i').classList.toggle('fa-eye-slash');
        });
    }

    // Handle modal form submissions
    const loginModal = document.getElementById('loginModal');
    const signupModal = document.getElementById('signupModal');

    if (loginModal) {
        const loginForm = loginModal.querySelector('form');
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            
            fetch(this.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => {
                if (response.ok) {
                    window.location.reload();
                } else {
                    return response.json().then(data => {
                        throw new Error(data.error || 'Login failed');
                    });
                }
            })
            .catch(error => {
                const alertDiv = document.createElement('div');
                alertDiv.className = 'alert alert-danger mt-3';
                alertDiv.textContent = error.message;
                loginForm.appendChild(alertDiv);
                setTimeout(() => alertDiv.remove(), 3000);
            });
        });
    }

    if (signupModal) {
        const signupForm = signupModal.querySelector('form');
        signupForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            
            fetch(this.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => {
                if (response.ok) {
                    return response.json();
                } else {
                    return response.json().then(data => {
                        throw new Error(data.error || 'Registration failed');
                    });
                }
            })
            .then(data => {
                // Close signup modal
                const modal = bootstrap.Modal.getInstance(signupModal);
                modal.hide();
                
                // Show success message
                const alertDiv = document.createElement('div');
                alertDiv.className = 'alert alert-success mt-3';
                alertDiv.textContent = data.message;
                document.querySelector('.container').insertBefore(alertDiv, document.querySelector('.container').firstChild);
                setTimeout(() => alertDiv.remove(), 3000);
                
                // Open login modal
                const loginModal = new bootstrap.Modal(document.getElementById('loginModal'));
                loginModal.show();
            })
            .catch(error => {
                const alertDiv = document.createElement('div');
                alertDiv.className = 'alert alert-danger mt-3';
                alertDiv.textContent = error.message;
                signupForm.appendChild(alertDiv);
                setTimeout(() => alertDiv.remove(), 3000);
            });
        });
    }
});

// Flash message auto-hide
document.addEventListener('DOMContentLoaded', function() {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 3000);
        }, 3000);
    });
});

// Add to cart animation
function addToCartAnimation(button) {
    button.classList.add('adding-to-cart');
    setTimeout(() => {
        button.classList.remove('adding-to-cart');
    }, 1000);
}

// Search functionality
const searchForm = document.querySelector('form[action*="search"]');
if (searchForm) {
    searchForm.addEventListener('submit', function(e) {
        const searchInput = this.querySelector('input[name="search"]');
        if (!searchInput.value.trim()) {
            e.preventDefault();
        }
    });
}

// Category filter
const categoryLinks = document.querySelectorAll('.dropdown-item[href*="category"]');
categoryLinks.forEach(link => {
    link.addEventListener('click', function(e) {
        e.preventDefault();
        const category = this.getAttribute('href').split('=')[1];
        window.location.href = `/category/${category}`;
    });
}); 