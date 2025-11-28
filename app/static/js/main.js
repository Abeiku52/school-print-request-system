/**
 * Main JavaScript for School Print Request System
 */

// Wait for DOM to be ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initMobileMenu();
    initUserDropdown();
    initAlertClose();
    initTooltips();
});

/**
 * Mobile Menu Toggle
 */
function initMobileMenu() {
    const mobileMenuToggle = document.getElementById('mobileMenuToggle');
    const navbarMenu = document.getElementById('navbarMenu');
    
    if (mobileMenuToggle && navbarMenu) {
        mobileMenuToggle.addEventListener('click', function() {
            this.classList.toggle('active');
            navbarMenu.classList.toggle('active');
            document.body.classList.toggle('menu-open');
        });
        
        // Close menu when clicking outside
        document.addEventListener('click', function(event) {
            if (!event.target.closest('.navbar')) {
                mobileMenuToggle.classList.remove('active');
                navbarMenu.classList.remove('active');
                document.body.classList.remove('menu-open');
            }
        });
    }
}

/**
 * User Dropdown Menu
 */
function initUserDropdown() {
    const userMenuButton = document.getElementById('userMenuButton');
    const userDropdownMenu = document.getElementById('userDropdownMenu');
    
    if (userMenuButton && userDropdownMenu) {
        userMenuButton.addEventListener('click', function(e) {
            e.stopPropagation();
            userDropdownMenu.classList.toggle('show');
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', function(event) {
            if (!event.target.closest('.user-dropdown')) {
                userDropdownMenu.classList.remove('show');
            }
        });
    }
}

/**
 * Alert Close Buttons
 */
function initAlertClose() {
    const alertCloseButtons = document.querySelectorAll('.alert-close');
    
    alertCloseButtons.forEach(button => {
        button.addEventListener('click', function() {
            const alert = this.closest('.alert');
            if (alert) {
                alert.classList.add('fade-out');
                setTimeout(() => {
                    alert.remove();
                }, 300);
            }
        });
    });
    
    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            if (alert.parentElement) {
                alert.classList.add('fade-out');
                setTimeout(() => {
                    alert.remove();
                }, 300);
            }
        }, 5000);
    });
}

/**
 * Initialize Tooltips
 */
function initTooltips() {
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    
    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', function() {
            const tooltipText = this.getAttribute('data-tooltip');
            const tooltip = document.createElement('div');
            tooltip.className = 'tooltip';
            tooltip.textContent = tooltipText;
            document.body.appendChild(tooltip);
            
            const rect = this.getBoundingClientRect();
            tooltip.style.top = (rect.top - tooltip.offsetHeight - 5) + 'px';
            tooltip.style.left = (rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2)) + 'px';
            
            this._tooltip = tooltip;
        });
        
        element.addEventListener('mouseleave', function() {
            if (this._tooltip) {
                this._tooltip.remove();
                this._tooltip = null;
            }
        });
    });
}

/**
 * Confirm Dialog
 */
function confirmAction(message) {
    return confirm(message);
}

/**
 * Show Loading Spinner
 */
function showLoading(element) {
    if (element) {
        element.classList.add('loading');
        element.disabled = true;
    }
}

/**
 * Hide Loading Spinner
 */
function hideLoading(element) {
    if (element) {
        element.classList.remove('loading');
        element.disabled = false;
    }
}

/**
 * Format File Size
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

/**
 * Debounce Function
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Copy to Clipboard
 */
function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            showNotification('Copied to clipboard!', 'success');
        }).catch(err => {
            console.error('Failed to copy:', err);
        });
    } else {
        // Fallback for older browsers
        const textarea = document.createElement('textarea');
        textarea.value = text;
        textarea.style.position = 'fixed';
        textarea.style.opacity = '0';
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);
        showNotification('Copied to clipboard!', 'success');
    }
}

/**
 * Show Notification
 */
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type} fade-in`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : 'info-circle'}"></i>
        <span>${message}</span>
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.add('fade-out');
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 3000);
}

/**
 * File Upload Handler - Multiple Files Support
 */
document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.querySelector('.form-control-file');
    const fileDisplay = document.querySelector('.file-display');
    const fileUploadLabel = document.querySelector('.file-upload-label');
    const fileUploadWrapper = document.querySelector('.file-upload-wrapper');
    const fileCountInfo = document.querySelector('.file-count-info');
    const fileCountText = document.getElementById('fileCountText');
    
    if (fileInput && fileDisplay) {
        fileInput.addEventListener('change', function(e) {
            const files = Array.from(e.target.files);
            const maxFiles = 10;
            
            if (files.length > maxFiles) {
                showNotification(`Maximum ${maxFiles} files allowed. Only first ${maxFiles} will be uploaded.`, 'error');
                // Keep only first 10 files
                const dt = new DataTransfer();
                for (let i = 0; i < maxFiles; i++) {
                    dt.items.add(files[i]);
                }
                fileInput.files = dt.files;
                return;
            }
            
            if (files.length > 0) {
                // Show files info
                let filesHTML = '';
                let totalSize = 0;
                
                files.forEach((file, index) => {
                    const fileSize = file.size;
                    totalSize += fileSize;
                    const fileName = file.name;
                    const fileExtension = fileName.split('.').pop().toUpperCase();
                    
                    filesHTML += `
                        <div style="display: flex; align-items: center; gap: 12px; padding: 12px; background: rgba(0, 82, 165, 0.03); border-radius: 8px; margin-bottom: 8px;">
                            <i class="fas fa-file-${getFileIcon(fileExtension)}" style="font-size: 1.5rem; color: var(--primary);"></i>
                            <div style="flex: 1;">
                                <div style="font-weight: 600; color: var(--text-primary); font-size: 0.9rem; margin-bottom: 2px;">
                                    ${fileName}
                                </div>
                                <div style="font-size: 0.8rem; color: var(--text-secondary);">
                                    ${fileExtension} • ${formatFileSize(fileSize)}
                                </div>
                            </div>
                            <i class="fas fa-check-circle" style="font-size: 1.25rem; color: var(--success);"></i>
                        </div>
                    `;
                });
                
                fileDisplay.innerHTML = filesHTML;
                fileDisplay.style.display = 'block';
                
                // Update file count
                if (fileCountInfo && fileCountText) {
                    fileCountText.textContent = `${files.length} file${files.length > 1 ? 's' : ''} selected (${formatFileSize(totalSize)} total)`;
                    fileCountInfo.style.display = 'block';
                }
                
                // Update upload area
                if (fileUploadWrapper) {
                    fileUploadWrapper.style.borderColor = 'var(--success)';
                    fileUploadWrapper.style.background = 'linear-gradient(135deg, rgba(16, 185, 129, 0.05) 0%, rgba(0, 82, 165, 0.03) 100%)';
                }
                
                if (fileUploadLabel) {
                    fileUploadLabel.innerHTML = `
                        <i class="fas fa-check-circle" style="font-size: 3rem; color: var(--success); margin-bottom: 12px; display: block;"></i>
                        <span style="display: block; font-size: 1.1rem; font-weight: 600; color: var(--success); margin-bottom: 4px;">
                            ${files.length} File${files.length > 1 ? 's' : ''} Uploaded Successfully!
                        </span>
                        <small style="display: block; color: var(--text-secondary); font-size: 0.9rem;">
                            Click to change files
                        </small>
                    `;
                }
                
                // Show success notification
                showNotification(`${files.length} file${files.length > 1 ? 's' : ''} uploaded successfully!`, 'success');
            }
        });
        
        // Drag and drop support
        if (fileUploadWrapper) {
            fileUploadWrapper.addEventListener('dragover', function(e) {
                e.preventDefault();
                this.style.borderColor = 'var(--primary)';
                this.style.background = 'linear-gradient(135deg, rgba(0, 82, 165, 0.1) 0%, rgba(255, 209, 0, 0.08) 100%)';
            });
            
            fileUploadWrapper.addEventListener('dragleave', function(e) {
                e.preventDefault();
                this.style.borderColor = 'rgba(0, 82, 165, 0.3)';
                this.style.background = 'linear-gradient(135deg, rgba(0, 82, 165, 0.02) 0%, rgba(255, 209, 0, 0.02) 100%)';
            });
            
            fileUploadWrapper.addEventListener('drop', function(e) {
                e.preventDefault();
                this.style.borderColor = 'rgba(0, 82, 165, 0.3)';
                this.style.background = 'linear-gradient(135deg, rgba(0, 82, 165, 0.02) 0%, rgba(255, 209, 0, 0.02) 100%)';
                
                if (e.dataTransfer.files.length > 0) {
                    fileInput.files = e.dataTransfer.files;
                    fileInput.dispatchEvent(new Event('change'));
                }
            });
        }
    }
});

/**
 * Get File Icon based on extension
 */
function getFileIcon(extension) {
    const icons = {
        'PDF': 'pdf',
        'DOC': 'word',
        'DOCX': 'word',
        'XLS': 'excel',
        'XLSX': 'excel',
        'PPT': 'powerpoint',
        'PPTX': 'powerpoint',
        'TXT': 'alt',
        'ZIP': 'archive',
        'RAR': 'archive'
    };
    
    return icons[extension] || 'alt';
}

/**
 * Calculate Total Pages
 */
document.addEventListener('DOMContentLoaded', function() {
    const pagesInput = document.querySelector('input[name="number_of_pages"]');
    const copiesInput = document.querySelector('input[name="number_of_copies"]');
    const totalDisplay = document.querySelector('.total-pages-display');
    
    if (pagesInput && copiesInput && totalDisplay) {
        function updateTotal() {
            const pages = parseInt(pagesInput.value) || 0;
            const copies = parseInt(copiesInput.value) || 0;
            const total = pages * copies;
            
            if (total > 0) {
                totalDisplay.querySelector('strong').textContent = total;
                totalDisplay.style.display = 'block';
            } else {
                totalDisplay.style.display = 'none';
            }
        }
        
        pagesInput.addEventListener('input', updateTotal);
        copiesInput.addEventListener('input', updateTotal);
    }
});
