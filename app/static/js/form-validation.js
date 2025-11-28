/**
 * Client-side form validation helpers
 */

// File upload validation
function validateFileUpload(fileInput, allowedExtensions, maxSizeMB) {
    const file = fileInput.files[0];
    
    if (!file) {
        return { valid: false, message: 'Please select a file' };
    }
    
    // Check file extension
    const fileName = file.name.toLowerCase();
    const fileExt = fileName.split('.').pop();
    
    if (!allowedExtensions.includes(fileExt)) {
        return { 
            valid: false, 
            message: `Invalid file type. Allowed: ${allowedExtensions.join(', ')}` 
        };
    }
    
    // Check file size
    const fileSizeMB = file.size / (1024 * 1024);
    if (fileSizeMB > maxSizeMB) {
        return { 
            valid: false, 
            message: `File size (${fileSizeMB.toFixed(1)}MB) exceeds ${maxSizeMB}MB limit` 
        };
    }
    
    return { valid: true, message: 'File is valid' };
}

// Display file information after selection
function displayFileInfo(fileInput, displayElement) {
    const file = fileInput.files[0];
    
    if (file) {
        const fileSizeMB = (file.size / (1024 * 1024)).toFixed(2);
        const fileInfo = `
            <div class="file-info">
                <strong>Selected file:</strong> ${file.name}<br>
                <strong>Size:</strong> ${fileSizeMB} MB
            </div>
        `;
        displayElement.innerHTML = fileInfo;
        displayElement.style.display = 'block';
    } else {
        displayElement.style.display = 'none';
    }
}

// Validate number input range
function validateNumberRange(input, min, max) {
    const value = parseInt(input.value);
    
    if (isNaN(value)) {
        return { valid: false, message: 'Please enter a valid number' };
    }
    
    if (value < min) {
        return { valid: false, message: `Value must be at least ${min}` };
    }
    
    if (value > max) {
        return { valid: false, message: `Value must not exceed ${max}` };
    }
    
    return { valid: true, message: 'Valid' };
}

// Calculate and display total pages
function calculateTotalPages(pagesInput, copiesInput, displayElement) {
    const pages = parseInt(pagesInput.value) || 0;
    const copies = parseInt(copiesInput.value) || 0;
    const total = pages * copies;
    
    if (displayElement && total > 0) {
        displayElement.textContent = `Total pages to print: ${total}`;
        displayElement.style.display = 'block';
    }
}

// Show/hide form errors
function showFieldError(fieldElement, message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'field-error';
    errorDiv.textContent = message;
    
    // Remove existing error
    const existingError = fieldElement.parentElement.querySelector('.field-error');
    if (existingError) {
        existingError.remove();
    }
    
    // Add new error
    fieldElement.parentElement.appendChild(errorDiv);
    fieldElement.classList.add('error');
}

function clearFieldError(fieldElement) {
    const errorDiv = fieldElement.parentElement.querySelector('.field-error');
    if (errorDiv) {
        errorDiv.remove();
    }
    fieldElement.classList.remove('error');
}

// Form submission validation
function validatePrintRequestForm(form) {
    let isValid = true;
    const errors = [];
    
    // Validate file upload
    const fileInput = form.querySelector('input[type="file"][name="file"]');
    if (fileInput) {
        const fileValidation = validateFileUpload(fileInput, ['pdf', 'doc', 'docx'], 50);
        if (!fileValidation.valid) {
            showFieldError(fileInput, fileValidation.message);
            errors.push(fileValidation.message);
            isValid = false;
        } else {
            clearFieldError(fileInput);
        }
    }
    
    // Validate number of pages
    const pagesInput = form.querySelector('input[name="number_of_pages"]');
    if (pagesInput) {
        const pagesValidation = validateNumberRange(pagesInput, 1, 1000);
        if (!pagesValidation.valid) {
            showFieldError(pagesInput, pagesValidation.message);
            errors.push(pagesValidation.message);
            isValid = false;
        } else {
            clearFieldError(pagesInput);
        }
    }
    
    // Validate number of copies
    const copiesInput = form.querySelector('input[name="number_of_copies"]');
    if (copiesInput) {
        const copiesValidation = validateNumberRange(copiesInput, 1, 100);
        if (!copiesValidation.valid) {
            showFieldError(copiesInput, copiesValidation.message);
            errors.push(copiesValidation.message);
            isValid = false;
        } else {
            clearFieldError(copiesInput);
        }
    }
    
    return { valid: isValid, errors: errors };
}

// Initialize form validation on page load
document.addEventListener('DOMContentLoaded', function() {
    // File upload preview
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            const displayElement = this.parentElement.querySelector('.file-display');
            if (displayElement) {
                displayFileInfo(this, displayElement);
            }
        });
    });
    
    // Real-time total pages calculation
    const pagesInput = document.querySelector('input[name="number_of_pages"]');
    const copiesInput = document.querySelector('input[name="number_of_copies"]');
    const totalDisplay = document.querySelector('.total-pages-display');
    
    if (pagesInput && copiesInput && totalDisplay) {
        pagesInput.addEventListener('input', function() {
            calculateTotalPages(pagesInput, copiesInput, totalDisplay);
        });
        
        copiesInput.addEventListener('input', function() {
            calculateTotalPages(pagesInput, copiesInput, totalDisplay);
        });
    }
    
    // Form submission validation
    const printRequestForm = document.querySelector('form.print-request-form');
    if (printRequestForm) {
        printRequestForm.addEventListener('submit', function(e) {
            const validation = validatePrintRequestForm(this);
            if (!validation.valid) {
                e.preventDefault();
                alert('Please fix the errors in the form before submitting.');
            }
        });
    }
});
