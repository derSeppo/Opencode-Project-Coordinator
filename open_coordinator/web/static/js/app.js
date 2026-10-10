// OpenCode AI Coordinator - Web Interface JavaScript

// Global state
let state = {
    tasks: [],
    currentTaskId: null,
    messages: [],
    providers: {},
    stats: null,
    isLoading: false,
    apiKey: localStorage.getItem('apiKey') || '',
    selectedProvider: localStorage.getItem('selectedProvider') || 'auto',
    selectedModel: localStorage.getItem('selectedModel') || '',
    temperature: parseFloat(localStorage.getItem('temperature')) || 0.7,
    maxTokens: parseInt(localStorage.getItem('maxTokens')) || 2000
};

// API Configuration
const API_BASE = window.location.origin || 'http://localhost:8000';
const API_KEY_HEADER = 'X-API-Key';

// DOM Elements
const elements = {
    statsGrid: document.getElementById('stats-grid'),
    providersGrid: document.getElementById('providers-grid'),
    chatContainer: document.getElementById('chat-container'),
    chatMessages: document.getElementById('chat-messages'),
    chatInput: document.getElementById('chat-input'),
    sendButton: document.getElementById('send-button'),
    taskList: document.getElementById('task-list'),
    apiKeyInput: document.getElementById('api-key-input'),
    saveApiKeyBtn: document.getElementById('save-api-key'),
    providerSelect: document.getElementById('provider-select'),
    modelSelect: document.getElementById('model-select'),
    temperatureInput: document.getElementById('temperature-input'),
    maxTokensInput: document.getElementById('max-tokens-input'),
    taskTypeSelect: document.getElementById('task-type-select'),
    codeLanguageSelect: document.getElementById('code-language-select'),
    executeBtn: document.getElementById('execute-btn'),
    clearChatBtn: document.getElementById('clear-chat-btn'),
    newChatBtn: document.getElementById('new-chat-btn')
};

// Initialize the application
async function init() {
    console.log('Initializing OpenCode AI Coordinator Web UI...');
    
    // Load saved state
    loadState();
    
    // Setup event listeners
    setupEventListeners();
    
    // Load initial data
    await loadProviders();
    await loadStats();
    await loadTasks();
    
    // Update UI
    updateProviderSelect();
    updateApiKeyUI();
    
    console.log('OpenCode AI Coordinator Web UI initialized');
}

// Load saved state from localStorage
function loadState() {
    state.apiKey = localStorage.getItem('apiKey') || '';
    state.selectedProvider = localStorage.getItem('selectedProvider') || 'auto';
    state.selectedModel = localStorage.getItem('selectedModel') || '';
    state.temperature = parseFloat(localStorage.getItem('temperature')) || 0.7;
    state.maxTokens = parseInt(localStorage.getItem('maxTokens')) || 2000;
}

// Save state to localStorage
function saveState() {
    localStorage.setItem('apiKey', state.apiKey);
    localStorage.setItem('selectedProvider', state.selectedProvider);
    localStorage.setItem('selectedModel', state.selectedModel);
    localStorage.setItem('temperature', state.temperature.toString());
    localStorage.setItem('maxTokens', state.maxTokens.toString());
}

// Setup event listeners
function setupEventListeners() {
    // Save API key
    if (elements.saveApiKeyBtn) {
        elements.saveApiKeyBtn.addEventListener('click', saveApiKey);
    }
    
    // Provider select change
    if (elements.providerSelect) {
        elements.providerSelect.addEventListener('change', (e) => {
            state.selectedProvider = e.target.value;
            saveState();
            updateModelSelect();
        });
    }
    
    // Model select change
    if (elements.modelSelect) {
        elements.modelSelect.addEventListener('change', (e) => {
            state.selectedModel = e.target.value;
            saveState();
        });
    }
    
    // Temperature change
    if (elements.temperatureInput) {
        elements.temperatureInput.addEventListener('change', (e) => {
            state.temperature = parseFloat(e.target.value);
            saveState();
        });
    }
    
    // Max tokens change
    if (elements.maxTokensInput) {
        elements.maxTokensInput.addEventListener('change', (e) => {
            state.maxTokens = parseInt(e.target.value);
            saveState();
        });
    }
    
    // Send message
    if (elements.sendButton && elements.chatInput) {
        elements.sendButton.addEventListener('click', sendMessage);
        elements.chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
    }
    
    // Execute button
    if (elements.executeBtn) {
        elements.executeBtn.addEventListener('click', executeTask);
    }
    
    // Clear chat
    if (elements.clearChatBtn) {
        elements.clearChatBtn.addEventListener('click', clearChat);
    }
    
    // New chat
    if (elements.newChatBtn) {
        elements.newChatBtn.addEventListener('click', newChat);
    }
    
    // Task type change
    if (elements.taskTypeSelect) {
        elements.taskTypeSelect.addEventListener('change', updateTaskForm);
    }
    
    // Auto-refresh tasks every 5 seconds
    setInterval(loadTasks, 5000);
    
    // Auto-refresh stats every 30 seconds
    setInterval(loadStats, 30000);
}

// Save API key
function saveApiKey() {
    if (elements.apiKeyInput) {
        state.apiKey = elements.apiKeyInput.value;
        saveState();
        updateApiKeyUI();
        showAlert('API key saved!', 'success');
    }
}

// Update API key UI
function updateApiKeyUI() {
    if (elements.apiKeyInput) {
        elements.apiKeyInput.value = state.apiKey;
    }
}

// Make API request
async function apiRequest(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    const headers = {
        'Content-Type': 'application/json',
        ...(state.apiKey && { [API_KEY_HEADER]: state.apiKey })
    };
    
    try {
        const response = await fetch(url, {
            headers,
            ...options
        });
        
        if (!response.ok) {
            if (response.status === 401) {
                throw new Error('Unauthorized - Please check your API key');
            }
            const error = await response.json();
            throw new Error(error.error || error.detail || `HTTP ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        showAlert(error.message || 'An error occurred', 'error');
        throw error;
    }
}

// Load providers
async function loadProviders() {
    try {
        state.providers = await apiRequest('/providers');
        renderProviders();
        updateProviderSelect();
    } catch (error) {
        console.error('Failed to load providers:', error);
    }
}

// Render providers
function renderProviders() {
    if (!elements.providersGrid) return;
    
    elements.providersGrid.innerHTML = Object.entries(state.providers).map(([name, provider]) => {
        const isFree = provider.models && provider.models.some(m => m.free);
        const isEnabled = provider.enabled;
        const freeBadge = isFree ? '<span class="free-badge">FREE</span>' : '';
        
        return `
            <div class="provider-card ${isEnabled ? 'enabled' : 'disabled'}" data-provider="${name}">
                <div class="provider-header">
                    <div class="provider-name">${name}</div>
                    <div class="provider-status ${isEnabled ? 'enabled' : 'disabled'}">
                        ${isEnabled ? 'Enabled' : 'Disabled'}
                    </div>
                    ${freeBadge}
                </div>
                <div class="provider-info">
                    Base URL: ${provider.base_url}
                </div>
                <div class="provider-models">
                    ${provider.models && provider.models.length > 0 ? 
                        provider.models.slice(0, 3).map(m => 
                            `<span class="provider-model">${m.id || m}</span>`
                        ).join('') : 
                        '<span class="provider-model">No models</span>'
                    }
                    ${provider.models && provider.models.length > 3 ? 
                        `<span class="provider-model">+${provider.models.length - 3} more</span>` : ''}
                </div>
                <div class="provider-meta">
                    <span>Rate Limit: ${provider.rate_limit}</span>
                    <span>Timeout: ${provider.timeout}s</span>
                </div>
            </div>
        `;
    }).join('');
    
    // Add click handlers
    document.querySelectorAll('.provider-card').forEach(card => {
        card.addEventListener('click', () => {
            const provider = card.dataset.provider;
            state.selectedProvider = provider;
            saveState();
            updateProviderSelect();
            updateModelSelect();
            showAlert(`Selected provider: ${provider}`, 'info');
        });
    });
}

// Update provider select dropdown
function updateProviderSelect() {
    if (!elements.providerSelect) return;
    
    const providers = Object.keys(state.providers || {});
    const enabledProviders = providers.filter(p => state.providers[p].enabled);
    
    elements.providerSelect.innerHTML = `
        <option value="auto">Auto (Best Available)</option>
        ${enabledProviders.map(p => 
            `<option value="${p}" ${state.selectedProvider === p ? 'selected' : ''}>${p}</option>`
        ).join('')}
    `;
}

// Update model select dropdown
async function updateModelSelect() {
    if (!elements.modelSelect) return;
    
    try {
        let models = [];
        
        if (state.selectedProvider && state.selectedProvider !== 'auto') {
            // Get models for selected provider
            const providerModels = await apiRequest(`/providers/${state.selectedProvider}/models`);
            models = providerModels || [];
        } else {
            // Get all models
            const allModels = await apiRequest('/models');
            models = allModels || [];
        }
        
        elements.modelSelect.innerHTML = `
            <option value="">Default Model</option>
            ${models.map(m => 
                `<option value="${m.id || m}" ${state.selectedModel === (m.id || m) ? 'selected' : ''}>
                    ${m.id || m} ${m.free ? '(FREE)' : ''}
                </option>`
            ).join('')}
        `;
    } catch (error) {
        console.error('Failed to load models:', error);
    }
}

// Load stats
async function loadStats() {
    try {
        state.stats = await apiRequest('/stats');
        renderStats();
    } catch (error) {
        console.error('Failed to load stats:', error);
    }
}

// Render stats
function renderStats() {
    if (!elements.statsGrid || !state.stats) return;
    
    const stats = [
        { label: 'Total Tasks', value: state.stats.total_tasks, key: 'total_tasks' },
        { label: 'Completed', value: state.stats.completed_tasks, key: 'completed_tasks' },
        { label: 'Failed', value: state.stats.failed_tasks, key: 'failed_tasks' },
        { label: 'Total Tokens', value: state.stats.total_tokens.toLocaleString(), key: 'total_tokens' },
        { label: 'Total Cost', value: `$${state.stats.total_cost.toFixed(2)}`, key: 'total_cost' },
        { label: 'Avg Time', value: `${Math.round(state.stats.avg_execution_time_ms)}ms`, key: 'avg_time' }
    ];
    
    elements.statsGrid.innerHTML = stats.map(stat => `
        <div class="stat-card fade-in">
            <h3>${stat.label}</h3>
            <div class="value">${stat.value}</div>
            <div class="label">${stat.key.replace('_', ' ')}</div>
        </div>
    `).join('');
}

// Load tasks
async function loadTasks() {
    try {
        const response = await apiRequest('/tasks?limit=10');
        state.tasks = response.tasks || [];
        renderTasks();
    } catch (error) {
        console.error('Failed to load tasks:', error);
    }
}

// Render tasks
function renderTasks() {
    if (!elements.taskList) return;
    
    elements.taskList.innerHTML = state.tasks.map(task => {
        const statusClass = task.status.toLowerCase();
        const providerName = task.provider_used || 'N/A';
        const modelName = task.model_used || 'N/A';
        
        return `
            <div class="task-item fade-in" data-task-id="${task.task_id}">
                <div class="task-info">
                    <div class="task-id">${task.task_id.substring(0, 8)}...</div>
                    <div class="task-status ${statusClass}">${task.status}</div>
                    <div class="task-preview">${truncateText(task.result || task.prompt || '', 50)}</div>
                </div>
                <div class="task-meta">
                    <span>${providerName}</span>
                    <span>${modelName}</span>
                    <span>${task.tokens_used} tokens</span>
                </div>
            </div>
        `;
    }).join('');
    
    // Add click handlers
    document.querySelectorAll('.task-item').forEach(item => {
        item.addEventListener('click', () => {
            const taskId = item.dataset.taskId;
            loadTaskDetails(taskId);
        });
    });
}

// Load task details
async function loadTaskDetails(taskId) {
    try {
        const task = await apiRequest(`/task/${taskId}`);
        state.currentTaskId = taskId;
        
        // Display task in chat
        addMessage('system', `Task Details: ${task.task_id}`);
        addMessage('assistant', `Status: ${task.status}\nProvider: ${task.provider_used}\nModel: ${task.model_used}\nTokens: ${task.tokens_used}\nCost: $${task.cost.toFixed(4)}\nTime: ${task.execution_time_ms}ms`);
        
        if (task.result) {
            addMessage('assistant', task.result);
        }
        
        // Scroll to bottom
        scrollToBottom();
    } catch (error) {
        console.error('Failed to load task details:', error);
    }
}

// Send message
async function sendMessage() {
    if (!elements.chatInput || state.isLoading) return;
    
    const message = elements.chatInput.value.trim();
    if (!message) return;
    
    // Add user message
    addMessage('user', message);
    elements.chatInput.value = '';
    
    // Set loading state
    state.isLoading = true;
    toggleLoading(true);
    
    try {
        // Build request based on current settings
        const request = {
            task_type: elements.taskTypeSelect ? elements.taskTypeSelect.value : 'code_generation',
            prompt: message,
            language: elements.codeLanguageSelect ? elements.codeLanguageSelect.value : 'python',
            temperature: state.temperature,
            max_tokens: state.maxTokens
        };
        
        // Add provider preference if selected
        if (state.selectedProvider && state.selectedProvider !== 'auto') {
            request.provider_preference = [state.selectedProvider];
        }
        
        // Add model preference if selected
        if (state.selectedModel) {
            request.model_preference = state.selectedModel;
        }
        
        // Add code if it's a code task
        if (request.task_type !== 'code_generation') {
            // For now, just use the prompt as code
            request.code = message;
        }
        
        // Send request
        const response = await apiRequest('/task', {
            method: 'POST',
            body: JSON.stringify(request)
        });
        
        const taskId = response.task_id;
        state.currentTaskId = taskId;
        
        // Add system message about task creation
        addMessage('system', `Task created: ${taskId}`);
        
        // Poll for results
        await pollForTaskResult(taskId);
        
    } catch (error) {
        addMessage('assistant', `Error: ${error.message}`);
    } finally {
        state.isLoading = false;
        toggleLoading(false);
    }
}

// Poll for task result
async function pollForTaskResult(taskId) {
    let attempts = 0;
    const maxAttempts = 60; // Poll for 2 minutes
    
    while (attempts < maxAttempts) {
        await new Promise(resolve => setTimeout(resolve, 2000));
        
        try {
            const task = await apiRequest(`/task/${taskId}`);
            
            if (task.status === 'completed') {
                addMessage('assistant', task.result || 'Task completed with no result');
                break;
            } else if (task.status === 'failed') {
                addMessage('assistant', `Task failed: ${task.error || 'Unknown error'}`);
                break;
            }
            
            // Update the system message with status
            updateLastSystemMessage(`Task ${taskId}: ${task.status}`);
            
        } catch (error) {
            console.error('Polling error:', error);
        }
        
        attempts++;
    }
    
    if (attempts >= maxAttempts) {
        addMessage('assistant', 'Task timed out. Please check the task list.');
    }
    
    scrollToBottom();
}

// Update last system message
function updateLastSystemMessage(text) {
    const messages = elements.chatMessages.querySelectorAll('.chat-message');
    if (messages.length > 0) {
        const lastSystem = [...messages].reverse().find(m => m.classList.contains('system'));
        if (lastSystem) {
            lastSystem.textContent = text;
        }
    }
}

// Execute task
async function executeTask() {
    if (!elements.taskTypeSelect || state.isLoading) return;
    
    const taskType = elements.taskTypeSelect.value;
    const prompt = elements.chatInput ? elements.chatInput.value.trim() : '';
    
    if (!prompt) {
        showAlert('Please enter a prompt', 'warning');
        return;
    }
    
    state.isLoading = true;
    toggleLoading(true);
    
    try {
        const request = {
            task_type: taskType,
            prompt: prompt,
            language: elements.codeLanguageSelect ? elements.codeLanguageSelect.value : 'python',
            temperature: state.temperature,
            max_tokens: state.maxTokens
        };
        
        if (state.selectedProvider && state.selectedProvider !== 'auto') {
            request.provider_preference = [state.selectedProvider];
        }
        
        if (state.selectedModel) {
            request.model_preference = state.selectedModel;
        }
        
        if (taskType !== 'code_generation' && taskType !== 'explanation') {
            request.code = prompt;
        }
        
        const response = await apiRequest('/execute?wait=true&timeout=60', {
            method: 'POST',
            body: JSON.stringify(request)
        });
        
        if (response.result) {
            addMessage('user', prompt);
            addMessage('assistant', response.result);
            elements.chatInput.value = '';
        } else if (response.task_id) {
            addMessage('user', prompt);
            addMessage('system', `Task created: ${response.task_id}`);
            await pollForTaskResult(response.task_id);
        }
        
    } catch (error) {
        addMessage('assistant', `Error: ${error.message}`);
    } finally {
        state.isLoading = false;
        toggleLoading(false);
        scrollToBottom();
    }
}

// Add message to chat
function addMessage(role, content) {
    if (!elements.chatMessages) return;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${role} fade-in`;
    
    // Format content (handle newlines and code blocks)
    const formattedContent = formatMessage(content);
    messageDiv.innerHTML = formattedContent;
    
    elements.chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

// Format message content
function formatMessage(content) {
    if (!content) return '';
    
    // Escape HTML
    let formatted = escapeHtml(content);
    
    // Format code blocks
    formatted = formatted.replace(/```(\w*)\n?([\s\S]*?)```/g, (match, lang, code) => {
        return `<div class="code-block"><pre><code class="language-${lang}">${code.trim()}</code></pre></div>`;
    });
    
    // Format inline code
    formatted = formatted.replace(/`([^`]+)`/g, '<code>$1</code>');
    
    // Format line breaks
    formatted = formatted.replace(/\n/g, '<br>');
    
    return formatted;
}

// Escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Truncate text
function truncateText(text, maxLength) {
    if (!text) return '';
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

// Scroll to bottom
function scrollToBottom() {
    if (elements.chatMessages) {
        elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;
    }
}

// Toggle loading state
function toggleLoading(loading) {
    if (elements.sendButton) {
        elements.sendButton.disabled = loading;
        elements.sendButton.innerHTML = loading ? '<span class="spinner"></span> Sending...' : 'Send';
    }
    if (elements.executeBtn) {
        elements.executeBtn.disabled = loading;
        elements.executeBtn.innerHTML = loading ? '<span class="spinner"></span> Executing...' : 'Execute';
    }
}

// Clear chat
function clearChat() {
    if (elements.chatMessages) {
        elements.chatMessages.innerHTML = '';
    }
    state.currentTaskId = null;
    showAlert('Chat cleared', 'info');
}

// New chat
function newChat() {
    clearChat();
    state.messages = [];
    showAlert('New chat started', 'info');
}

// Update task form based on task type
function updateTaskForm() {
    // Could show/hide different form elements based on task type
}

// Show alert
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} fade-in`;
    alertDiv.innerHTML = `<span>${message}</span>`;
    
    // Find a place to insert the alert
    const container = document.querySelector('.main-container') || document.body;
    container.insertBefore(alertDiv, container.firstChild);
    
    // Remove after 5 seconds
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// Check API connectivity
async function checkApiHealth() {
    try {
        await apiRequest('/health');
        return true;
    } catch (error) {
        return false;
    }
}

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', init);
