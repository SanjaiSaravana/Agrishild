// Authentication utility functions

function getToken() {
    return localStorage.getItem('token');
}

function isLoggedIn() {
    return !!getToken();
}

function logout() {
    localStorage.removeItem('token');
    window.location.href = '/login';
}

function requireAuth() {
    if (!isLoggedIn()) {
        // Store the current page to redirect back after login
        localStorage.setItem('redirectAfterLogin', window.location.pathname);
        window.location.href = '/login';
    }
}

function updateNavigation() {
    const navRight = document.querySelector('.nav-right');
    if (!navRight) return;

    if (isLoggedIn()) {
        // Show logout button
        navRight.innerHTML = `
            <span style="color: var(--primary); margin-right: 15px; font-size: 0.9rem;">Welcome!</span>
            <button onclick="logout()" class="btn-logout">Logout</button>
        `;
    } else {
        // Show login/signup buttons
        navRight.innerHTML = `
            <a href="/login" class="nav-link" style="margin-right: 15px;">Login</a>
            <a href="/signup" class="btn-signup">Sign Up</a>
        `;
    }
}

// Auto-update navigation on page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', updateNavigation);
} else {
    updateNavigation();
}
