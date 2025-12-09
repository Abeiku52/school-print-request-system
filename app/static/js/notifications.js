/**
 * Notification Bell Component
 * Handles fetching, displaying, and managing user notifications
 */

class NotificationBell {
    constructor() {
        this.bellButton = document.getElementById('notificationBell');
        this.dropdown = document.getElementById('notificationDropdown');
        this.badge = document.getElementById('notificationBadge');
        this.notificationList = document.getElementById('notificationList');
        this.markAllReadBtn = document.getElementById('markAllRead');
        
        this.isOpen = false;
        this.notifications = [];
        this.unreadCount = 0;
        
        if (this.bellButton) {
            this.init();
        }
    }
    
    init() {
        // Event listeners
        this.bellButton.addEventListener('click', (e) => {
            e.stopPropagation();
            this.toggleDropdown();
        });
        
        if (this.markAllReadBtn) {
            this.markAllReadBtn.addEventListener('click', () => {
                this.markAllAsRead();
            });
        }
        
        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (this.isOpen && !this.dropdown.contains(e.target)) {
                this.closeDropdown();
            }
        });
        
        // Initial fetch
        this.fetchNotifications();
        
        // Poll for new notifications every 30 seconds
        setInterval(() => {
            this.fetchNotifications();
        }, 30000);
    }
    
    async fetchNotifications() {
        try {
            const response = await fetch('/requests/api/notifications/unread', {
                headers: {
                    'Content-Type': 'application/json'
                },
                credentials: 'same-origin'
            });
            
            if (!response.ok) {
                throw new Error('Failed to fetch notifications');
            }
            
            const data = await response.json();
            this.notifications = data.notifications || [];
            this.unreadCount = data.count || 0;
            
            this.updateBadge();
            
            // If dropdown is open, update the list
            if (this.isOpen) {
                this.renderNotifications();
            }
        } catch (error) {
            console.error('Error fetching notifications:', error);
        }
    }
    
    updateBadge() {
        if (this.unreadCount > 0) {
            this.badge.textContent = this.unreadCount > 99 ? '99+' : this.unreadCount;
            this.badge.style.display = 'block';
        } else {
            this.badge.style.display = 'none';
        }
        
        // Show/hide mark all read button
        if (this.markAllReadBtn) {
            this.markAllReadBtn.style.display = this.unreadCount > 0 ? 'flex' : 'none';
        }
    }
    
    toggleDropdown() {
        if (this.isOpen) {
            this.closeDropdown();
        } else {
            this.openDropdown();
        }
    }
    
    openDropdown() {
        this.dropdown.style.display = 'block';
        this.isOpen = true;
        this.renderNotifications();
    }
    
    closeDropdown() {
        this.dropdown.style.display = 'none';
        this.isOpen = false;
    }
    
    renderNotifications() {
        if (this.notifications.length === 0) {
            this.notificationList.innerHTML = `
                <div class="notification-empty">
                    <i class="fas fa-bell-slash"></i>
                    <h4>No notifications</h4>
                    <p>You're all caught up!</p>
                </div>
            `;
            return;
        }
        
        const notificationsHTML = this.notifications.map(notification => {
            return this.createNotificationItem(notification);
        }).join('');
        
        this.notificationList.innerHTML = notificationsHTML;
        
        // Add click handlers to notification items
        this.notificationList.querySelectorAll('.notification-item').forEach(item => {
            item.addEventListener('click', () => {
                const notificationId = parseInt(item.dataset.notificationId);
                const requestId = parseInt(item.dataset.requestId);
                this.handleNotificationClick(notificationId, requestId);
            });
        });
    }
    
    createNotificationItem(notification) {
        const timeAgo = this.getTimeAgo(notification.created_at);
        const statusClass = notification.status.toLowerCase().replace(' ', '_');
        const iconMap = {
            'pending': 'fa-clock',
            'in_progress': 'fa-spinner',
            'processing': 'fa-cog',
            'completed': 'fa-check-circle',
            'cancelled': 'fa-times-circle'
        };
        const icon = iconMap[statusClass] || 'fa-bell';
        
        return `
            <div class="notification-item ${notification.is_read ? '' : 'unread'}" 
                 data-notification-id="${notification.id}"
                 data-request-id="${notification.request_id}">
                <div class="notification-content">
                    <div class="notification-icon status-${statusClass}">
                        <i class="fas ${icon}"></i>
                    </div>
                    <div class="notification-body">
                        <div class="notification-message">${this.escapeHtml(notification.message)}</div>
                        <div class="notification-meta">
                            <span class="notification-time">
                                <i class="fas fa-clock"></i>
                                ${timeAgo}
                            </span>
                            <span class="notification-status-badge ${statusClass}">
                                ${this.formatStatus(notification.status)}
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    async handleNotificationClick(notificationId, requestId) {
        // Mark as read
        await this.markAsRead(notificationId);
        
        // Navigate to request details
        window.location.href = `/requests/${requestId}`;
    }
    
    async markAsRead(notificationId) {
        try {
            const response = await fetch(`/requests/api/notifications/${notificationId}/read`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                credentials: 'same-origin'
            });
            
            if (response.ok) {
                // Update local state
                const notification = this.notifications.find(n => n.id === notificationId);
                if (notification) {
                    notification.is_read = true;
                }
                
                this.unreadCount = Math.max(0, this.unreadCount - 1);
                this.updateBadge();
                this.renderNotifications();
            }
        } catch (error) {
            console.error('Error marking notification as read:', error);
        }
    }
    
    async markAllAsRead() {
        try {
            const response = await fetch('/requests/api/notifications/read-all', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                credentials: 'same-origin'
            });
            
            if (response.ok) {
                // Update local state
                this.notifications.forEach(n => n.is_read = true);
                this.unreadCount = 0;
                this.updateBadge();
                this.renderNotifications();
            }
        } catch (error) {
            console.error('Error marking all notifications as read:', error);
        }
    }
    
    getTimeAgo(timestamp) {
        const now = new Date();
        const notificationTime = new Date(timestamp);
        const diffInSeconds = Math.floor((now - notificationTime) / 1000);
        
        if (diffInSeconds < 60) {
            return 'Just now';
        } else if (diffInSeconds < 3600) {
            const minutes = Math.floor(diffInSeconds / 60);
            return `${minutes} ${minutes === 1 ? 'minute' : 'minutes'} ago`;
        } else if (diffInSeconds < 86400) {
            const hours = Math.floor(diffInSeconds / 3600);
            return `${hours} ${hours === 1 ? 'hour' : 'hours'} ago`;
        } else if (diffInSeconds < 604800) {
            const days = Math.floor(diffInSeconds / 86400);
            return `${days} ${days === 1 ? 'day' : 'days'} ago`;
        } else {
            return notificationTime.toLocaleDateString();
        }
    }
    
    formatStatus(status) {
        const statusMap = {
            'pending': 'Pending',
            'in_progress': 'In Progress',
            'processing': 'Processing',
            'completed': 'Completed',
            'cancelled': 'Cancelled'
        };
        return statusMap[status] || status;
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize notification bell when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.notificationBell = new NotificationBell();
});
