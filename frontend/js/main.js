/* Main JavaScript */

// ===== Responsive Menu Functions =====
function toggleMobileMenu() {
    const mobileNav = document.getElementById('mobileNav');
    const hamburger = document.querySelector('.hamburger');
    if (mobileNav && hamburger) {
        mobileNav.classList.toggle('active');
        hamburger.classList.toggle('active');
    }
}

function closeMobileMenu() {
    const mobileNav = document.getElementById('mobileNav');
    const hamburger = document.querySelector('.hamburger');
    if (mobileNav && hamburger) {
        mobileNav.classList.remove('active');
        hamburger.classList.remove('active');
    }
}

function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    if (sidebar) {
        sidebar.classList.toggle('active');
    }
}

function closeSidebar() {
    const sidebar = document.querySelector('.sidebar');
    if (sidebar) {
        sidebar.classList.remove('active');
    }
}

// Close mobile menu when clicking on links
document.addEventListener('DOMContentLoaded', function() {
    const mobileNavLinks = document.querySelectorAll('.mobile-nav a');
    mobileNavLinks.forEach(link => {
        link.addEventListener('click', closeMobileMenu);
    });
    
    const sidebarLinks = document.querySelectorAll('.sidebar a');
    sidebarLinks.forEach(link => {
        link.addEventListener('click', closeSidebar);
    });
});

// Store token
let authToken = null;

// Check if user is logged in
function isLoggedIn() {
    return localStorage.getItem('token') !== null;
}

// Handle login
async function handleLogin(event) {
    event.preventDefault();
    
    const username = document.getElementById('loginUsername').value;
    const password = document.getElementById('loginPassword').value;
    
    try {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.status === 'success') {
            localStorage.setItem('token', data.data.access_token);
            authToken = data.data.access_token;
            closeLogin();
            showNotification('Login successful!', 'success');
            setTimeout(() => {
                window.location.href = 'dashboard.html';
            }, 1000);
        } else {
            showNotification(data.message, 'error');
        }
    } catch (error) {
        showNotification('Login failed', 'error');
    }
}

// Handle registration
async function handleRegister(event) {
    event.preventDefault();
    
    const username = document.getElementById('regUsername').value;
    const email = document.getElementById('regEmail').value;
    const password = document.getElementById('regPassword').value;
    
    try {
        const response = await fetch('/api/auth/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, email, password })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.status === 'success') {
            closeRegister();
            showNotification('Registration successful! Please login.', 'success');
        } else {
            showNotification(data.message, 'error');
        }
    } catch (error) {
        showNotification('Registration failed', 'error');
    }
}

// Handle logout
function handleLogout() {
    localStorage.removeItem('token');
    authToken = null;
    showNotification('Logged out successfully', 'success');
    setTimeout(() => {
        window.location.href = 'index.html';
    }, 500);
}

// Show notification
function showNotification(message, type) {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'}"></i>
        <span>${message}</span>
    `;
    document.body.appendChild(notification);
    
    notification.style.animation = 'slideIn 0.3s ease';
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 4000);
}

// Modal functions
function showLogin() {
    document.getElementById('loginModal').style.display = 'flex';
}

function closeLogin() {
    document.getElementById('loginModal').style.display = 'none';
    document.getElementById('loginUsername').value = '';
    document.getElementById('loginPassword').value = '';
}

function showRegister() {
    document.getElementById('registerModal').style.display = 'flex';
}

function closeRegister() {
    document.getElementById('registerModal').style.display = 'none';
    document.getElementById('regUsername').value = '';
    document.getElementById('regEmail').value = '';
    document.getElementById('regPassword').value = '';
}

// Scroll to features
function scrollToFeatures() {
    const element = document.getElementById('features');
    if (element) {
        element.scrollIntoView({ behavior: 'smooth' });
    }
}

// Navigate to page - show login if not authenticated
function navigateToPage(page) {
    if (isLoggedIn()) {
        window.location.href = page;
    } else {
        // Show login modal instead of redirecting
        showLogin();
        showNotification('Please login to access this page', 'error');
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    // Check auth status
    authToken = localStorage.getItem('token');
    
    if (isLoggedIn()) {
        // Update UI for logged in user
        const authButtons = document.querySelector('.nav-auth');
        if (authButtons) {
            const loginBtn = authButtons.querySelector('.btn-login');
            const registerBtn = authButtons.querySelector('.btn-register');
            if (loginBtn && registerBtn && !authButtons.querySelector('.btn-logout')) {
                authButtons.innerHTML = `
                    <button class="btn-logout" onclick="handleLogout()">
                        <i class="fas fa-sign-out-alt"></i> Logout
                    </button>
                `;
            }
        }
        
        // Redirect if on index
        if (window.location.pathname === '/' || window.location.pathname.endsWith('index.html')) {
            // Already on index, allow access
        }
    } else {
        // Immediately redirect to index if not logged in and on protected pages
        const protectedPages = ['dashboard.html', 'defect-detection.html', 'cost-prediction.html', 'analytics.html'];
        const currentPage = window.location.pathname.split('/').pop();
        
        if (protectedPages.includes(currentPage)) {
            // Redirect immediately without delay
            window.location.href = 'index.html';
            return;
        }
    }
    
    // Close modals when clicking outside
    window.onclick = (event) => {
        if (event.target.classList.contains('modal')) {
            event.target.style.display = 'none';
        }
    };
});
