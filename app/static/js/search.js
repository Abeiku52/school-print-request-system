/**
 * Search functionality for requests
 */

document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('requestSearch');
    
    if (!searchInput) return;
    
    searchInput.addEventListener('input', (e) => {
        const searchTerm = e.target.value.toLowerCase();
        const requestCards = document.querySelectorAll('.request-card');
        
        requestCards.forEach(card => {
            const requestNumber = card.querySelector('.request-number')?.textContent.toLowerCase() || '';
            const fileName = card.querySelector('.info-item span')?.textContent.toLowerCase() || '';
            const status = card.querySelector('.badge')?.textContent.toLowerCase() || '';
            
            const matches = requestNumber.includes(searchTerm) || 
                          fileName.includes(searchTerm) || 
                          status.includes(searchTerm);
            
            if (matches) {
                card.style.display = '';
                card.classList.add('fade-in');
            } else {
                card.style.display = 'none';
            }
        });
    });
});
