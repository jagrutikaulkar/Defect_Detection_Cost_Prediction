/* Dashboard JavaScript - User-Friendly Version */

// Load dashboard data on page load
document.addEventListener('DOMContentLoaded', () => {
    // Always show welcome section
    showWelcomeSection();
});

// Show welcome section for new users
function showWelcomeSection() {
    const welcomeSection = document.getElementById('welcomeSection');
    
    if (welcomeSection) welcomeSection.style.display = 'block';
}
