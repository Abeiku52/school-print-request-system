/**
 * Sidebar Navigation
 * Handles hamburger menu and sidebar toggle with persistent state
 */

document.addEventListener('DOMContentLoaded', () => {
    const hamburgerMenu = document.getElementById('hamburgerMenu');
    const sidebarNav = document.getElementById('sidebarNav');
    const sidebarClose = document.getElementById('sidebarClose');
    const sidebarOverlay = document.getElementById('sidebarOverlay');
    
    if (!hamburgerMenu || !sidebarNav) return;
    
    // Check if sidebar should be open from localStorage
    const sidebarState = localStorage.getItem('sidebarOpen');
    
    // Open sidebar
    function openSidebar() {
        sidebarNav.classList.add('active');
        sidebarOverlay.classList.add('active');
        hamburgerMenu.classList.add('active');
        document.body.classList.add('sidebar-open');
        localStorage.setItem('sidebarOpen', 'true');
        
        // Only prevent body scroll on mobile
        if (window.innerWidth <= 768) {
            document.body.style.overflow = 'hidden';
            document.body.classList.remove('sidebar-open');
        }
    }
    
    // Close sidebar
    function closeSidebar() {
        sidebarNav.classList.remove('active');
        sidebarOverlay.classList.remove('active');
        hamburgerMenu.classList.remove('active');
        document.body.classList.remove('sidebar-open');
        document.body.style.overflow = '';
        localStorage.setItem('sidebarOpen', 'false');
    }
    
    // Restore sidebar state on page load
    if (sidebarState === 'true') {
        openSidebar();
    }
    
    // Toggle sidebar
    hamburgerMenu.addEventListener('click', (e) => {
        e.stopPropagation();
        if (sidebarNav.classList.contains('active')) {
            closeSidebar();
        } else {
            openSidebar();
        }
    });
    
    // Close button
    if (sidebarClose) {
        sidebarClose.addEventListener('click', closeSidebar);
    }
    
    // Overlay click
    if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', closeSidebar);
    }
    
    // Close on escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && sidebarNav.classList.contains('active')) {
            closeSidebar();
        }
    });
    
    // Don't close sidebar when clicking links (keep it open for navigation)
    // Only close on mobile
    const sidebarLinks = document.querySelectorAll('.sidebar-link');
    sidebarLinks.forEach(link => {
        link.addEventListener('click', () => {
            if (window.innerWidth <= 768) {
                closeSidebar();
            }
        });
    });
    
    // Handle window resize
    window.addEventListener('resize', () => {
        if (window.innerWidth > 768) {
            document.body.style.overflow = '';
        } else if (sidebarNav.classList.contains('active')) {
            document.body.style.overflow = 'hidden';
        }
    });
});
