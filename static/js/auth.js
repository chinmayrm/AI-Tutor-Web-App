// Authentication JavaScript
document.addEventListener('DOMContentLoaded', function() {
    initializeAuth();
});

// DOM Elements
const tabBtns = document.querySelectorAll('.tab-btn');
const authForms = document.querySelectorAll('.auth-form');
const loginForm = document.getElementById('loginForm');
const signupForm = document.getElementById('signupForm');
const passwordToggles = document.querySelectorAll('.toggle-password');
const signupPassword = document.getElementById('signupPassword');
const confirmPassword = document.getElementById('confirmPassword');
const passwordStrength = document.getElementById('passwordStrength');
const loadingOverlay = document.getElementById('loadingOverlay');

function initializeAuth() {
    // Tab switching
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => switchTab(btn.dataset.tab));
    });

    // Form submissions
    loginForm.addEventListener('submit', handleLogin);
    signupForm.addEventListener('submit', handleSignup);

    // Password visibility toggles
    passwordToggles.forEach(toggle => {
        toggle.addEventListener('click', () => togglePasswordVisibility(toggle));
    });

    // Password strength checking
    if (signupPassword) {
        signupPassword.addEventListener('input', checkPasswordStrength);
    }

    // Password confirmation checking
    if (confirmPassword) {
        confirmPassword.addEventListener('input', checkPasswordMatch);
    }

    // Check if user is already logged in
    checkAuthStatus();
}

function switchTab(tabName) {
    // Update tab buttons
    tabBtns.forEach(btn => {
        btn.classList.toggle('active', btn.dataset.tab === tabName);
    });

    // Update forms
    authForms.forEach(form => {
        form.classList.toggle('active', form.id === `${tabName}-form`);
    });

    // Clear any error messages
    clearErrors();
}

function togglePasswordVisibility(toggle) {
    const targetId = toggle.dataset.target;
    const targetInput = document.getElementById(targetId);
    const icon = toggle.querySelector('i');

    if (targetInput.type === 'password') {
        targetInput.type = 'text';
        icon.className = 'fas fa-eye-slash';
    } else {
        targetInput.type = 'password';
        icon.className = 'fas fa-eye';
    }
}

function checkPasswordStrength() {
    const password = signupPassword.value;
    const strength = calculatePasswordStrength(password);
    
    let strengthText = '';
    let strengthClass = '';

    if (password.length === 0) {
        passwordStrength.innerHTML = '';
        return;
    }

    if (strength < 30) {
        strengthText = 'Weak password';
        strengthClass = 'strength-weak';
    } else if (strength < 60) {
        strengthText = 'Medium password';
        strengthClass = 'strength-medium';
    } else {
        strengthText = 'Strong password';
        strengthClass = 'strength-strong';
    }

    passwordStrength.innerHTML = `<span class="${strengthClass}">💪 ${strengthText}</span>`;
}

function calculatePasswordStrength(password) {
    let strength = 0;
    
    // Length
    if (password.length >= 8) strength += 20;
    if (password.length >= 12) strength += 10;
    
    // Character types
    if (/[a-z]/.test(password)) strength += 15;
    if (/[A-Z]/.test(password)) strength += 15;
    if (/[0-9]/.test(password)) strength += 15;
    if (/[^A-Za-z0-9]/.test(password)) strength += 25;
    
    return Math.min(strength, 100);
}

function checkPasswordMatch() {
    const password = signupPassword.value;
    const confirm = confirmPassword.value;
    
    if (confirm.length === 0) return;
    
    if (password !== confirm) {
        confirmPassword.setCustomValidity('Passwords do not match');
        confirmPassword.style.borderColor = '#dc3545';
    } else {
        confirmPassword.setCustomValidity('');
        confirmPassword.style.borderColor = '#28a745';
    }
}

async function handleLogin(e) {
    e.preventDefault();
    
    const formData = new FormData(loginForm);
    const email = formData.get('email');
    const password = formData.get('password');
    const rememberMe = document.getElementById('rememberMe').checked;

    if (!validateEmail(email)) {
        showToast('Please enter a valid email address', 'error');
        return;
    }

    showLoading(true);
    
    try {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                email: email,
                password: password,
                remember: rememberMe
            })
        });

        const data = await response.json();

        if (response.ok && data.success) {
            showToast('Login successful! Welcome back!', 'success');
            setTimeout(() => {
                window.location.href = '/';
            }, 1500);
        } else {
            showToast(data.message || 'Login failed. Please check your credentials.', 'error');
        }
    } catch (error) {
        console.error('Login error:', error);
        showToast('Network error. Please try again.', 'error');
    } finally {
        showLoading(false);
    }
}

async function handleSignup(e) {
    e.preventDefault();
    
    const formData = new FormData(signupForm);
    const name = formData.get('name').trim();
    const email = formData.get('email');
    const password = formData.get('password');
    const confirmPass = formData.get('confirmPassword');
    const agreeTerms = document.getElementById('agreeTerms').checked;

    // Validation
    if (!name || name.length < 2) {
        showToast('Please enter a valid full name', 'error');
        return;
    }

    if (!validateEmail(email)) {
        showToast('Please enter a valid email address', 'error');
        return;
    }

    if (password.length < 6) {
        showToast('Password must be at least 6 characters long', 'error');
        return;
    }

    if (password !== confirmPass) {
        showToast('Passwords do not match', 'error');
        return;
    }

    if (!agreeTerms) {
        showToast('Please agree to the Terms of Service and Privacy Policy', 'error');
        return;
    }

    showLoading(true);
    
    try {
        const response = await fetch('/api/auth/signup', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                name: name,
                email: email,
                password: password
            })
        });

        const data = await response.json();

        if (response.ok && data.success) {
            showToast('Account created successfully! Welcome to AI Personal Tutor!', 'success');
            setTimeout(() => {
                window.location.href = '/';
            }, 1500);
        } else {
            showToast(data.message || 'Signup failed. Please try again.', 'error');
        }
    } catch (error) {
        console.error('Signup error:', error);
        showToast('Network error. Please try again.', 'error');
    } finally {
        showLoading(false);
    }
}

async function continueAsGuest() {
    showLoading(true);
    
    try {
        const response = await fetch('/api/auth/guest', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        const data = await response.json();

        if (response.ok && data.success) {
            showToast('Welcome! Starting your learning journey...', 'success');
            setTimeout(() => {
                window.location.href = '/';
            }, 1500);
        } else {
            showToast('Unable to continue as guest. Please try again.', 'error');
        }
    } catch (error) {
        console.error('Guest login error:', error);
        showToast('Network error. Please try again.', 'error');
    } finally {
        showLoading(false);
    }
}

function validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function showLoading(show) {
    if (show) {
        loadingOverlay.classList.remove('hidden');
    } else {
        loadingOverlay.classList.add('hidden');
    }
}

function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icon = {
        success: 'fas fa-check-circle',
        error: 'fas fa-exclamation-circle',
        warning: 'fas fa-exclamation-triangle',
        info: 'fas fa-info-circle'
    }[type];

    toast.innerHTML = `
        <div style="display: flex; align-items: center; gap: 10px;">
            <i class="${icon}" style="color: var(--${type}-color, #333);"></i>
            <span>${message}</span>
        </div>
    `;

    toastContainer.appendChild(toast);

    // Auto remove after 5 seconds
    setTimeout(() => {
        toast.style.animation = 'slideOutRight 0.3s ease-out forwards';
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }, 5000);
}

function clearErrors() {
    const inputs = document.querySelectorAll('input');
    inputs.forEach(input => {
        input.style.borderColor = '';
        input.setCustomValidity('');
    });
}

async function checkAuthStatus() {
    try {
        const response = await fetch('/api/auth/status');
        const data = await response.json();
        
        if (data.authenticated) {
            // User is already logged in, redirect to main app
            window.location.href = '/';
        }
    } catch (error) {
        // Continue with login page if check fails
        console.log('Auth status check failed, continuing with login page');
    }
}

// Add CSS animations for slide out
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOutRight {
        from {
            opacity: 1;
            transform: translateX(0);
        }
        to {
            opacity: 0;
            transform: translateX(100%);
        }
    }
`;
document.head.appendChild(style);