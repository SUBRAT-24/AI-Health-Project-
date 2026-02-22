// Authentication JavaScript

document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const signupForm = document.getElementById('signupForm');

    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }

    if (signupForm) {
        signupForm.addEventListener('submit', handleSignup);
    }
});

async function handleLogin(e) {
    e.preventDefault();

    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    if (!email || !password) {
        showAlert('Please fill in all fields', 'error');
        return;
    }

    // Call the login function from main.js
    await window.healthAssistant.login(email, password);
}

async function handleSignup(e) {
    e.preventDefault();

    const fullname = document.getElementById('fullname').value;
    const email = document.getElementById('email').value;
    const phone = document.getElementById('phone').value;
    const dob = document.getElementById('dob').value;
    const gender = document.getElementById('gender').value;
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirmPassword').value;

    // Validation
    if (!fullname || !email || !phone || !dob || !gender || !password || !confirmPassword) {
        showAlert('Please fill in all fields', 'error');
        return;
    }

    if (password !== confirmPassword) {
        showAlert('Passwords do not match', 'error');
        return;
    }

    if (password.length < 6) {
        showAlert('Password must be at least 6 characters long', 'error');
        return;
    }

    const userData = {
        name: fullname,
        email: email,
        phone: phone,
        dob: dob,
        gender: gender,
        password: password
    };

    // Call the signup function from main.js
    await window.healthAssistant.signup(userData);
}

function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;
    alertDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 10000;
        min-width: 300px;
        padding: 1rem;
        border-radius: 4px;
        animation: slideInRight 0.3s ease-out;
    `;
    
    // Set background color based on type
    if (type === 'success') {
        alertDiv.style.backgroundColor = '#4caf50';
        alertDiv.style.color = 'white';
    } else if (type === 'error') {
        alertDiv.style.backgroundColor = '#f44336';
        alertDiv.style.color = 'white';
    } else {
        alertDiv.style.backgroundColor = '#2196F3';
        alertDiv.style.color = 'white';
    }
    
    document.body.appendChild(alertDiv);
    
    setTimeout(() => {
        alertDiv.style.animation = 'slideInLeft 0.3s ease-out reverse';
        setTimeout(() => {
            alertDiv.remove();
        }, 300);
    }, 4000);
}
