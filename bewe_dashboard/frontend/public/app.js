// Configuration
const API_BASE_URL = 'https://api.booking.novaxtreme.com/integrations/chatwoot/bewe/dashboard'; // Replace with your API Gateway URL

// DOM Elements
const worksList = document.getElementById('works-list');
const errorMessage = document.getElementById('error-message');
const loadingIndicator = document.getElementById('loading');

// Status mapping for display
const STATUS_MAP = {
    'res': 'Reserved',
    'confirmed': 'Confirmed',
    'res_missing': 'Missed',
    'res_client_rejected': 'Cancelled'
};

// Format date for display
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const options = { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    return new Date(dateString).toLocaleString(undefined, options);
}

// Show error message
function showError(message) {
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';
    worksList.innerHTML = '';
}

// Hide error message
function hideError() {
    errorMessage.style.display = 'none';
}

// Show loading state
function showLoading() {
    loadingIndicator.style.display = 'block';
    worksList.innerHTML = '';
    hideError();
}

// Hide loading state
function hideLoading() {
    loadingIndicator.style.display = 'none';
}

// Render works list
function renderWorks(works) {
    if (!works || works.length === 0) {
        worksList.innerHTML = '<div class="no-works">No recent works found</div>';
        return;
    }

    worksList.innerHTML = works.map(work => `
        <div class="work-item">
            <div class="work-header">
                <span class="work-id">#${work.id}</span>
                <span class="work-status status-${work.status.toLowerCase()}">${STATUS_MAP[work.status] || work.status}</span>
            </div>
            <div class="work-details">
                <p>Date: ${formatDate(work.work_time)}</p>
            </div>
        </div>
    `).join('');
}

// Fetch works from API
async function fetchWorks(contactId) {
    try {
        const response = await fetch(`${API_BASE_URL}?contact_id=${contactId}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        return data;
    } catch (error) {
        throw new Error(`Failed to fetch works: ${error.message}`);
    }
}

// Initialize the dashboard
async function initDashboard(contactId) {
    showLoading();
    
    try {
        const data = await fetchWorks(contactId);
        hideLoading();
        renderWorks(data.works);
    } catch (error) {
        hideLoading();
        showError(error.message);
    }
}

// Listen for Chatwoot app context
window.addEventListener("message", async function (event) {
    console.log('Received message event:', event.data); // Log the raw event data
    try {
        const eventData = JSON.parse(event.data);
        console.log('Parsed event data:', eventData); // Log the parsed data
        
        if (eventData.event === 'appContext') {
            console.log('Processing appContext event...'); // Log processing start
            const { contact } = eventData.data;
            
            if (!contact || !contact.id) {
                console.warn('No contact ID in appContext event.'); // Warn if no contact
                showError('No contact information available');
                return;
            }
            
            console.log('Contact ID found:', contact.id); // Log the ID
            await initDashboard(contact.id);
        }
    } catch (error) {
        // Ignore errors from non-JSON messages or other event types
        if (!(error instanceof SyntaxError)) {
            showError('Failed to process Chatwoot event');
            console.error('Error processing message event:', error);
        }
    }
});

// Request initial data from Chatwoot
window.parent.postMessage('chatwoot-dashboard-app:fetch-info', '*'); 