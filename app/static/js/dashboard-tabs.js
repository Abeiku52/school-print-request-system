/**
 * Dashboard Tabs Component
 * Handles tab switching and content display on the dashboard
 */

class DashboardTabs {
    constructor() {
        this.tabButtons = document.querySelectorAll('.tab-button');
        this.tabContents = document.querySelectorAll('.tab-content');
        this.activeTab = 'total';
        
        if (this.tabButtons.length > 0) {
            this.init();
        }
    }
    
    init() {
        // Add click handlers to tab buttons
        this.tabButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                const tabName = button.dataset.tab;
                this.switchTab(tabName);
            });
        });
        
        // Handle keyboard navigation
        this.tabButtons.forEach((button, index) => {
            button.addEventListener('keydown', (e) => {
                this.handleKeyboardNavigation(e, index);
            });
        });
        
        // Set initial active tab
        this.switchTab(this.activeTab);
    }
    
    switchTab(tabName) {
        // Don't do anything if already on this tab
        if (this.activeTab === tabName) {
            return;
        }
        
        // Update active tab
        this.activeTab = tabName;
        
        // Update button states
        this.tabButtons.forEach(button => {
            if (button.dataset.tab === tabName) {
                button.classList.add('active');
                button.setAttribute('aria-selected', 'true');
            } else {
                button.classList.remove('active');
                button.setAttribute('aria-selected', 'false');
            }
        });
        
        // Update content visibility
        this.tabContents.forEach(content => {
            if (content.id === `tab-${tabName}`) {
                content.classList.add('active');
                content.setAttribute('aria-hidden', 'false');
            } else {
                content.classList.remove('active');
                content.setAttribute('aria-hidden', 'true');
            }
        });
        
        // Update URL hash without scrolling
        if (history.pushState) {
            history.pushState(null, null, `#${tabName}`);
        } else {
            window.location.hash = tabName;
        }
    }
    
    handleKeyboardNavigation(event, currentIndex) {
        let newIndex = currentIndex;
        
        switch(event.key) {
            case 'ArrowLeft':
                event.preventDefault();
                newIndex = currentIndex > 0 ? currentIndex - 1 : this.tabButtons.length - 1;
                break;
            case 'ArrowRight':
                event.preventDefault();
                newIndex = currentIndex < this.tabButtons.length - 1 ? currentIndex + 1 : 0;
                break;
            case 'Home':
                event.preventDefault();
                newIndex = 0;
                break;
            case 'End':
                event.preventDefault();
                newIndex = this.tabButtons.length - 1;
                break;
            default:
                return;
        }
        
        // Focus and activate the new tab
        this.tabButtons[newIndex].focus();
        const tabName = this.tabButtons[newIndex].dataset.tab;
        this.switchTab(tabName);
    }
    
    getActiveTab() {
        return this.activeTab;
    }
}

// Initialize dashboard tabs when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.dashboardTabs = new DashboardTabs();
    
    // Check for hash in URL and switch to that tab
    if (window.location.hash) {
        const tabName = window.location.hash.substring(1);
        const validTabs = ['total', 'pending', 'in_progress', 'completed'];
        if (validTabs.includes(tabName)) {
            window.dashboardTabs.switchTab(tabName);
        }
    }
    
    // Handle browser back/forward buttons
    window.addEventListener('popstate', () => {
        if (window.location.hash) {
            const tabName = window.location.hash.substring(1);
            const validTabs = ['total', 'pending', 'in_progress', 'completed'];
            if (validTabs.includes(tabName)) {
                window.dashboardTabs.switchTab(tabName);
            }
        } else {
            window.dashboardTabs.switchTab('total');
        }
    });
});
