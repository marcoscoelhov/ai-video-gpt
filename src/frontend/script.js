/**
 * AI Video GPT Frontend JavaScript
 * 
 * Este arquivo contém toda a lógica de interação do frontend,
 * incluindo comunicação com a API, validação de formulário,
 * progresso em tempo real e gerenciamento de estados.
 */

// ===== CONFIGURAÇÕES E CONSTANTES =====
const API_BASE_URL = 'http://localhost:5000/api';
const POLL_INTERVAL = 2000; // 2 segundos
const MAX_RETRIES = 3;
const TOAST_DURATION = 5000; // 5 segundos

// Constantes de autenticação
const API_KEY_STORAGE_KEY = 'ai_video_gpt_api_key';
const DEFAULT_API_KEY = '7ffb1add-a5c8-4e47-b6ec-8c9a8f630aae'; // Chave padrão do .env

// ===== ELEMENTOS DO DOM =====
const elements = {
    // Formulário
    form: document.getElementById('video-form'),
    scriptInput: document.getElementById('script'),
    imagePromptsInput: document.getElementById('image-prompts'),
    generateBtn: document.getElementById('generate-btn'),
    charCount: document.getElementById('char-count'),
    
    // API Configuration
    apiKeyInput: document.getElementById('api-key'),
    apiKeyToggle: document.getElementById('api-key-toggle'),
    apiStatus: document.getElementById('api-status'),
    testApiKeyBtn: document.getElementById('test-api-key'),
    apiKeyModal: document.getElementById('api-key-modal'),
    modalApiKeyInput: document.getElementById('modal-api-key'),
    saveApiKeyBtn: document.getElementById('save-api-key-btn'),
    modalCloseBtn: document.getElementById('modal-close-btn'),
    
    // Seções
    generationSection: document.getElementById('generation-section'),
    progressSection: document.getElementById('progress-section'),
    resultSection: document.getElementById('result-section'),
    errorSection: document.getElementById('error-section'),
    
    // Progresso
    progressFill: document.getElementById('progress-fill'),
    progressPercentage: document.getElementById('progress-percentage'),
    currentStepText: document.getElementById('current-step-text'),
    
    // Resultado
    videoPlayer: document.getElementById('video-player'),
    downloadBtn: document.getElementById('download-btn'),
    newVideoBtn: document.getElementById('new-video-btn'),
    
    // Erro
    errorText: document.getElementById('error-text'),
    retryBtn: document.getElementById('retry-btn'),
    
    // Toast e Loading
    toast: document.getElementById('toast'),
    toastIcon: document.getElementById('toast-icon'),
    toastMessage: document.getElementById('toast-message'),
    toastClose: document.getElementById('toast-close'),
    loadingOverlay: document.getElementById('loading-overlay')
};

// ===== ESTADO DA APLICAÇÃO =====
let appState = {
    currentJobId: null,
    isGenerating: false,
    pollInterval: null,
    retryCount: 0,
    lastFormData: null,
    historyVisible: false,
    apiKey: null,
    authRequired: true,
    authChecked: false
};

// ===== HISTÓRICO =====
const HISTORY_STORAGE_KEY = 'ai_video_gpt_history';
const MAX_HISTORY_ITEMS = 20;

// ===== FUNÇÕES DE API KEY =====

/**
 * Obter API key do localStorage ou usar padrão
 */
function getApiKey() {
    const storedKey = localStorage.getItem(API_KEY_STORAGE_KEY);
    return storedKey || DEFAULT_API_KEY;
}

/**
 * Salvar API key no localStorage
 */
function saveApiKey(apiKey) {
    if (apiKey && apiKey.trim()) {
        localStorage.setItem(API_KEY_STORAGE_KEY, apiKey.trim());
        appState.apiKey = apiKey.trim();
        return true;
    }
    return false;
}

/**
 * Remover API key do localStorage
 */
function removeApiKey() {
    localStorage.removeItem(API_KEY_STORAGE_KEY);
    appState.apiKey = null;
}

/**
 * Mostrar modal de API key
 */
function showApiKeyModal() {
    if (elements.apiKeyModal) {
        elements.apiKeyModal.style.display = 'flex';
        if (elements.modalApiKeyInput) {
            elements.modalApiKeyInput.value = getApiKey();
            elements.modalApiKeyInput.focus();
        }
    }
}

/**
 * Ocultar modal de API key
 */
function hideApiKeyModal() {
    if (elements.apiKeyModal) {
        elements.apiKeyModal.style.display = 'none';
    }
}

/**
 * Atualizar status da API
 */
function updateApiStatus(status, message) {
    if (elements.apiStatus) {
        elements.apiStatus.textContent = message;
        elements.apiStatus.className = `api-status ${status}`;
    }
}

/**
 * Salvar item no histórico
 */
function saveToHistory(script, imagePrompts, effectsPreset = 'professional', enableEffects = true) {
    const historyItem = {
        id: Date.now().toString(),
        date: new Date().toISOString(),
        script: script,
        imagePrompts: imagePrompts,
        effectsPreset: effectsPreset,
        enableEffects: enableEffects,
        preview: {
            script: script.substring(0, 100) + (script.length > 100 ? '...' : ''),
            imagePrompts: imagePrompts.substring(0, 100) + (imagePrompts.length > 100 ? '...' : '')
        }
    };
    
    let history = getHistory();
    history.unshift(historyItem); // Adicionar no início
    
    // Limitar número de itens
    if (history.length > MAX_HISTORY_ITEMS) {
        history = history.slice(0, MAX_HISTORY_ITEMS);
    }
    
    localStorage.setItem(HISTORY_STORAGE_KEY, JSON.stringify(history));
    updateHistoryDisplay();
}

/**
 * Obter histórico do localStorage
 */
function getHistory() {
    try {
        const history = localStorage.getItem(HISTORY_STORAGE_KEY);
        return history ? JSON.parse(history) : [];
    } catch (error) {
        console.error('Erro ao carregar histórico:', error);
        return [];
    }
}

/**
 * Carregar item do histórico nos campos do formulário
 */
function loadFromHistory(historyItem) {
    elements.scriptInput.value = historyItem.script;
    elements.imagePromptsInput.value = historyItem.imagePrompts;
    
    // Carregar configurações de efeitos
    const effectsPresetSelect = document.getElementById('effects-preset');
    const enableEffectsCheckbox = document.getElementById('enable-effects');
    
    if (effectsPresetSelect) {
        effectsPresetSelect.value = historyItem.effectsPreset || 'professional';
    }
    
    if (enableEffectsCheckbox) {
        enableEffectsCheckbox.checked = historyItem.enableEffects ?? true;
    }
    
    // Atualizar contadores e descrições
    updateScriptCount();
    updatePromptsCount();
    updateEffectsDescription();
    
    // Focar no script
    elements.scriptInput.focus();
    
    showToast('Roteiro e prompts carregados do histórico!', 'success');
}

/**
 * Remover item do histórico
 */
function removeFromHistory(itemId) {
    let history = getHistory();
    history = history.filter(item => item.id !== itemId);
    localStorage.setItem(HISTORY_STORAGE_KEY, JSON.stringify(history));
    updateHistoryDisplay();
    showToast('Item removido do histórico', 'info');
}

/**
 * Limpar todo o histórico
 */
function clearHistory() {
    if (confirm('Tem certeza que deseja limpar todo o histórico? Esta ação não pode ser desfeita.')) {
        localStorage.removeItem(HISTORY_STORAGE_KEY);
        updateHistoryDisplay();
        showToast('Histórico limpo com sucesso', 'success');
    }
}

/**
 * Alternar visibilidade do histórico
 */
function toggleHistory() {
    const historyContent = document.getElementById('history-content');
    const toggleBtn = document.getElementById('toggle-history-btn');
    
    appState.historyVisible = !appState.historyVisible;
    
    if (appState.historyVisible) {
        historyContent.style.display = 'block';
        toggleBtn.innerHTML = `
            <span class="btn-icon">📋</span>
            <span class="btn-text">Ocultar Histórico</span>
        `;
        updateHistoryDisplay();
    } else {
        historyContent.style.display = 'none';
        toggleBtn.innerHTML = `
            <span class="btn-icon">📋</span>
            <span class="btn-text">Ver Histórico</span>
        `;
    }
}

/**
 * Atualizar exibição do histórico
 */
function updateHistoryDisplay() {
    const historyList = document.getElementById('history-list');
    const historyEmpty = document.getElementById('history-empty');
    const history = getHistory();
    
    if (history.length === 0) {
        historyEmpty.style.display = 'block';
        historyList.style.display = 'none';
        return;
    }
    
    historyEmpty.style.display = 'none';
    historyList.style.display = 'block';
    
    historyList.innerHTML = history.map(item => {
        const date = new Date(item.date);
        const formattedDate = date.toLocaleDateString('pt-BR', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
        
        return `
            <div class="history-item" data-id="${item.id}">
                <div class="history-item-header">
                    <span class="history-item-date">📅 ${formattedDate}</span>
                    <div class="history-item-actions">
                        <button class="history-action-btn" onclick="loadFromHistory(${JSON.stringify(item).replace(/"/g, '&quot;')})" title="Carregar">
                            📂
                        </button>
                        <button class="history-action-btn delete" onclick="removeFromHistory('${item.id}')" title="Excluir">
                            🗑️
                        </button>
                    </div>
                </div>
                <div class="history-item-content">
                    <div class="history-content-section">
                        <div class="history-content-label">
                            <span>🎭</span>
                            Roteiro
                        </div>
                        <div class="history-content-preview">${item.preview.script}</div>
                    </div>
                    <div class="history-content-section">
                        <div class="history-content-label">
                            <span>🎨</span>
                            Prompts de Imagem
                        </div>
                        <div class="history-content-preview">${item.preview.imagePrompts}</div>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

// ===== GERENCIAMENTO DE API KEY =====

/**
 * Salvar API key no localStorage
 */
function saveApiKey(apiKey) {
    if (apiKey) {
        localStorage.setItem(API_KEY_STORAGE_KEY, apiKey);
        appState.apiKey = apiKey;
    }
}

/**
 * Carregar API key do localStorage
 */
function loadApiKey() {
    let apiKey = localStorage.getItem(API_KEY_STORAGE_KEY);
    
    // Se não há API key salva, usar a padrão
    if (!apiKey) {
        apiKey = DEFAULT_API_KEY;
        saveApiKey(apiKey);
        console.log('🔑 API key padrão configurada automaticamente');
    }
    
    if (apiKey) {
        appState.apiKey = apiKey;
        if (elements.apiKeyInput) {
            elements.apiKeyInput.value = apiKey;
        }
        if (elements.modalApiKeyInput) {
            elements.modalApiKeyInput.value = apiKey;
        }
    }
    return apiKey;
}

/**
 * Limpar API key
 */
function clearApiKey() {
    localStorage.removeItem(API_KEY_STORAGE_KEY);
    appState.apiKey = null;
    if (elements.apiKeyInput) {
        elements.apiKeyInput.value = '';
    }
    if (elements.modalApiKeyInput) {
        elements.modalApiKeyInput.value = '';
    }
    updateApiStatus('disconnected', '🔴 Não configurada');
}

/**
 * Obter API key atual (localStorage > input > padrão)
 */
function getCurrentApiKey() {
    // Prioridade: estado da aplicação > localStorage > input de formulário > chave padrão
    return appState.apiKey || 
           localStorage.getItem(API_KEY_STORAGE_KEY) || 
           (elements.apiKeyInput && elements.apiKeyInput.value) ||
           DEFAULT_API_KEY;
}

/**
 * Atualizar status da API key na UI
 */
function updateApiStatus(status, message) {
    if (!elements.apiStatus) return;
    
    elements.apiStatus.className = `api-status ${status}`;
    elements.apiStatus.textContent = message;
    
    // Atualizar botão de teste
    if (elements.testApiKeyBtn) {
        elements.testApiKeyBtn.disabled = (status === 'testing');
        elements.testApiKeyBtn.textContent = status === 'testing' ? 'Testando...' : 'Testar Conexão';
    }
}

/**
 * Verificar se autenticação é necessária
 */
async function checkAuthRequirement() {
    try {
        const response = await fetch(`${API_BASE_URL}/auth/info`);
        const data = await response.json();
        
        appState.authRequired = data.authentication_required;
        appState.authChecked = true;
        
        // Se autenticação não for necessária, ocultar seção de API
        const apiConfigSection = document.getElementById('api-config-section');
        if (apiConfigSection) {
            apiConfigSection.style.display = appState.authRequired ? 'block' : 'none';
        }
        
        return data;
    } catch (error) {
        console.error('Erro ao verificar requisitos de autenticação:', error);
        appState.authRequired = true; // Assumir que autenticação é necessária em caso de erro
        return null;
    }
}

/**
 * Testar API key
 */
async function testApiKey(apiKey = null) {
    const keyToTest = apiKey || getCurrentApiKey();
    
    if (!keyToTest) {
        showToast('Por favor, insira uma API key para testar.', 'warning');
        return false;
    }
    
    updateApiStatus('testing', '🟡 Testando conexão...');
    
    try {
        const response = await fetch(`${API_BASE_URL}/auth/validate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-API-Key': keyToTest
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            updateApiStatus('connected', '🟢 Conectada e válida');
            
            // Salvar a chave se o teste foi bem-sucedido
            saveApiKey(keyToTest);
            
            showToast('API key válida! Conexão estabelecida.', 'success');
            return true;
        } else {
            const errorData = await response.json();
            updateApiStatus('disconnected', '🔴 Chave inválida');
            showToast(`API key inválida: ${errorData.message || 'Chave não autorizada'}`, 'error');
            return false;
        }
    } catch (error) {
        console.error('Erro ao testar API key:', error);
        updateApiStatus('disconnected', '🔴 Erro de conexão');
        showToast('Erro ao testar API key. Verifique a conexão.', 'error');
        return false;
    }
}

/**
 * Alternar visibilidade da API key
 */
function toggleApiKeyVisibility() {
    if (!elements.apiKeyInput) return;
    
    const isPassword = elements.apiKeyInput.type === 'password';
    elements.apiKeyInput.type = isPassword ? 'text' : 'password';
    
    if (elements.apiKeyToggle) {
        elements.apiKeyToggle.textContent = isPassword ? '🙈' : '👁️';
        elements.apiKeyToggle.title = isPassword ? 'Ocultar API Key' : 'Mostrar API Key';
    }
}

/**
 * Mostrar modal de API key
 */
function showApiKeyModal() {
    if (elements.apiKeyModal) {
        elements.apiKeyModal.style.display = 'flex';
        if (elements.modalApiKeyInput) {
            elements.modalApiKeyInput.focus();
        }
    }
}

/**
 * Ocultar modal de API key
 */
function hideApiKeyModal() {
    if (elements.apiKeyModal) {
        elements.apiKeyModal.style.display = 'none';
    }
}

/**
 * Salvar API key do modal
 */
async function saveApiKeyFromModal() {
    const apiKey = elements.modalApiKeyInput ? elements.modalApiKeyInput.value.trim() : '';
    
    if (!apiKey) {
        showToast('Por favor, insira uma API key.', 'warning');
        return;
    }
    
    const isValid = await testApiKey(apiKey);
    if (isValid) {
        // Atualizar input principal
        if (elements.apiKeyInput) {
            elements.apiKeyInput.value = apiKey;
        }
        hideApiKeyModal();
    }
}

// ===== UTILITÁRIOS =====

/**
 * Exibir toast de notificação
 */
function showToast(message, type = 'info', duration = TOAST_DURATION) {
    const icons = {
        success: '✅',
        error: '❌',
        warning: '⚠️',
        info: 'ℹ️'
    };
    
    elements.toastIcon.textContent = icons[type] || icons.info;
    elements.toastMessage.textContent = message;
    elements.toast.className = `toast ${type}`;
    elements.toast.classList.add('show');
    
    // Auto-hide após duração especificada
    setTimeout(() => {
        hideToast();
    }, duration);
}

/**
 * Ocultar toast
 */
function hideToast() {
    elements.toast.classList.remove('show');
}

/**
 * Exibir/ocultar loading overlay
 */
function showLoading(show = true) {
    elements.loadingOverlay.style.display = show ? 'flex' : 'none';
}

/**
 * Fazer requisição HTTP com tratamento de erro e autenticação
 */
async function makeRequest(url, options = {}) {
    try {
        // Preparar headers
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };
        
        // Adicionar API key se necessária e disponível
        const apiKey = getCurrentApiKey();
        if (appState.authRequired && apiKey) {
            headers['X-API-Key'] = apiKey;
        }
        
        console.log('Making request to:', url);
        console.log('Headers:', headers);
        
        const response = await fetch(url, {
            headers,
            ...options
        });
        
        console.log('Response status:', response.status);
        
        // Tratar erros de autenticação
        if (response.status === 401) {
            let errorData;
            try {
                errorData = await response.json();
            } catch (e) {
                errorData = { error: 'Erro de autenticação' };
            }
            
            // Se API key for obrigatória mas não fornecida
            if (appState.authRequired && !apiKey) {
                showApiKeyModal();
                throw new Error('API key é obrigatória. Configure uma chave válida.');
            }
            
            // Se API key for inválida
            updateApiStatus('disconnected', '🔴 Chave inválida');
            showToast('API key inválida. Verifique suas credenciais.', 'error');
            throw new Error(errorData.error || 'Não autorizado');
        }
        
        let data;
        try {
            data = await response.json();
        } catch (e) {
            console.error('Error parsing JSON response:', e);
            throw new Error(`Erro ao processar resposta do servidor: ${response.status}`);
        }
        
        if (!response.ok) {
            let errorMessage = `HTTP ${response.status}`;
            
            // Extrair mensagem de erro do objeto de resposta
            if (data.error) {
                if (typeof data.error === 'string') {
                    errorMessage = data.error;
                } else if (data.error.message) {
                    errorMessage = data.error.message;
                } else if (data.error.details && data.error.details.field_errors) {
                    // Tratar erros de validação de campos
                    const fieldErrors = Object.values(data.error.details.field_errors);
                    errorMessage = fieldErrors.join(', ');
                } else {
                    errorMessage = JSON.stringify(data.error);
                }
            } else if (data.message) {
                errorMessage = data.message;
            }
            
            console.error('API Error:', errorMessage);
            throw new Error(errorMessage);
        }
        
        return data;
    } catch (error) {
        console.error('Request failed:', error);
        // Melhorar a mensagem de erro para o usuário
        if (error.name === 'TypeError' && error.message.includes('fetch')) {
            throw new Error('Erro de conexão. Verifique se o servidor está rodando.');
        }
        throw error;
    }
}

/**
 * Verificar se a API está disponível
 */
async function checkApiHealth() {
    try {
        showLoading(true);
        await makeRequest(`${API_BASE_URL}/health`);
        showLoading(false);
        return true;
    } catch (error) {
        showLoading(false);
        showToast('Não foi possível conectar com o servidor. Verifique se a API está rodando.', 'error');
        return false;
    }
}

/**
 * Validar formulário
 */
function validateForm() {
    const script = elements.scriptInput.value.trim();
    const imagePrompts = elements.imagePromptsInput.value.trim();
    
    if (!script) {
        showToast('Por favor, insira um script para o vídeo.', 'warning');
        elements.scriptInput.focus();
        return false;
    }
    
    if (script.length < 50) {
        showToast('O script deve ter pelo menos 50 caracteres.', 'warning');
        elements.scriptInput.focus();
        return false;
    }
    
    if (!imagePrompts) {
        showToast('Por favor, insira os prompts de imagem.', 'warning');
        elements.imagePromptsInput.focus();
        return false;
    }
    
    if (imagePrompts.length < 50) {
        showToast('Os prompts de imagem devem ter pelo menos 50 caracteres.', 'warning');
        elements.imagePromptsInput.focus();
        return false;
    }
    
    return true;
}

/**
 * Coletar dados do formulário
 */
function getFormData() {
    const effectsPreset = document.getElementById('effects-preset')?.value || 'professional';
    const enableEffects = document.getElementById('enable-effects')?.checked ?? true;
    const imagePresetValue = document.getElementById('image-preset')?.value || '';
    
    // Garantir que image_preset seja um valor válido ou null
    const validPresets = ['3d_cartoon', 'realistic', 'anime', 'digital_art'];
    const imagePreset = validPresets.includes(imagePresetValue) ? imagePresetValue : '3d_cartoon';
    
    return {
        script: elements.scriptInput.value.trim(),
        image_prompts: elements.imagePromptsInput.value.trim(),
        voice_provider: 'elevenlabs',  // Valor padrão
        voice_type: 'narrator',       // Valor padrão
        language: 'pt',               // Valor padrão
        video_format: 'tiktok',       // Valor padrão
        effects_preset: effectsPreset,
        enable_effects: enableEffects,
        image_preset: imagePreset
    };
}

/**
 * Atualizar contador de caracteres (função mantida para compatibilidade)
 */
function updateCharCount() {
    // Função removida para evitar recursão infinita
    // Os contadores são atualizados diretamente pelos event listeners
}

/**
 * Atualizar contador de caracteres e cenas do script
 */
function updateScriptCount() {
    const scriptInput = document.getElementById('script');
    const scriptCharCount = document.getElementById('script-char-count');
    const sceneCount = document.getElementById('scene-count');
    
    if (scriptInput && scriptCharCount && sceneCount) {
        const text = scriptInput.value;
        const charLength = text.length;
        scriptCharCount.textContent = charLength;
        
        // Count scenes (lines with character names and voices)
        const scenePattern = /^.+\s*–\s*Voice:\s*.+$/gm;
        const scenes = text.match(scenePattern) || [];
        sceneCount.textContent = scenes.length;
        
        // Visual validation
        scriptInput.classList.remove('valid', 'invalid');
        if (scenes.length > 0 && charLength > 50) {
            scriptInput.classList.add('valid');
        } else if (charLength > 0) {
            scriptInput.classList.add('invalid');
        }
    }
}

/**
 * Atualizar contador de caracteres e cenas dos prompts de imagem
 */
function updatePromptsCount() {
    const promptsInput = document.getElementById('image-prompts');
    const promptsCharCount = document.getElementById('prompts-char-count');
    const promptsSceneCount = document.getElementById('prompts-scene-count');
    
    if (promptsInput && promptsCharCount && promptsSceneCount) {
        const text = promptsInput.value;
        const charLength = text.length;
        promptsCharCount.textContent = charLength;
        
        // Count prompts (lines starting with "Scene" or containing scene indicators)
        const promptPattern = /^Scene\s+\d+:|^\d+\.|^-\s*Scene/gmi;
        const prompts = text.match(promptPattern) || [];
        promptsSceneCount.textContent = prompts.length;
        
        // Visual validation
        promptsInput.classList.remove('valid', 'invalid');
        if (prompts.length > 0 && charLength > 50) {
            promptsInput.classList.add('valid');
        } else if (charLength > 0) {
            promptsInput.classList.add('invalid');
        }
    }
}

// ===== GERENCIAMENTO DE SEÇÕES =====

/**
 * Mostrar seção específica
 */
function showSection(sectionName) {
    // Ocultar todas as seções
    elements.generationSection.style.display = 'none';
    elements.progressSection.style.display = 'none';
    elements.resultSection.style.display = 'none';
    elements.errorSection.style.display = 'none';
    
    // Mostrar seção específica
    switch (sectionName) {
        case 'generation':
            elements.generationSection.style.display = 'block';
            break;
        case 'progress':
            elements.progressSection.style.display = 'block';
            break;
        case 'result':
            elements.resultSection.style.display = 'block';
            break;
        case 'error':
            elements.errorSection.style.display = 'block';
            break;
    }
}

/**
 * Atualizar progresso
 */
function updateProgress(percentage, step) {
    elements.progressFill.style.width = `${percentage}%`;
    elements.progressPercentage.textContent = `${percentage}%`;
    elements.currentStepText.textContent = step;
}

/**
 * Resetar estado da aplicação
 */
function resetAppState() {
    appState.currentJobId = null;
    appState.isGenerating = false;
    appState.retryCount = 0;
    
    if (appState.pollInterval) {
        clearInterval(appState.pollInterval);
        appState.pollInterval = null;
    }
    
    // Resetar UI
    elements.generateBtn.disabled = false;
    elements.generateBtn.innerHTML = `
        <span class="btn-icon">🚀</span>
        <span class="btn-text">Gerar Vídeo</span>
    `;
    
    updateProgress(0, 'Aguardando...');
}

// ===== GERAÇÃO DE VÍDEO =====

/**
 * Iniciar geração de vídeo
 */
async function startVideoGeneration(formData) {
    try {
        appState.isGenerating = true;
        appState.lastFormData = formData;
        
        // Verificar se temos API key quando necessário
        const apiKey = getApiKey();
        if (appState.authRequired && !apiKey) {
            showApiKeyModal();
            throw new Error('API key é obrigatória para gerar vídeos.');
        }
        
        // Atualizar UI
        elements.generateBtn.disabled = true;
        elements.generateBtn.innerHTML = `
            <span class="btn-icon">⏳</span>
            <span class="btn-text">Iniciando...</span>
        `;
        
        console.log('Starting video generation with data:', formData);
        
        // Fazer requisição para iniciar geração
        const response = await makeRequest(`${API_BASE_URL}/generate-video`, {
            method: 'POST',
            body: JSON.stringify(formData)
        });
        
        console.log('Video generation response:', response);
        
        if (!response.job_id) {
            throw new Error('Resposta inválida do servidor: job_id não encontrado');
        }
        
        appState.currentJobId = response.job_id;
        
        // Mostrar seção de progresso
        showSection('progress');
        updateProgress(5, 'Geração iniciada...');
        
        // Salvar no histórico
        const effectsPresetSelect = document.getElementById('effects-preset');
        const enableEffectsCheckbox = document.getElementById('enable-effects');
        const effectsPreset = effectsPresetSelect ? effectsPresetSelect.value : 'professional';
        const enableEffects = enableEffectsCheckbox ? enableEffectsCheckbox.checked : true;
        
        saveToHistory(
            formData.script || '',
            formData.image_prompts || '',
            effectsPreset,
            enableEffects
        );
        
        // Iniciar polling do status
        startStatusPolling();
        
        showToast('Geração de vídeo iniciada com sucesso!', 'success');
        
    } catch (error) {
        console.error('Error starting video generation:', error);
        let errorMessage = 'Erro desconhecido ao iniciar geração';
        
        if (error.message) {
            errorMessage = error.message;
        } else if (typeof error === 'string') {
            errorMessage = error;
        } else if (typeof error === 'object') {
            // Converter objeto de erro para string legível
            errorMessage = JSON.stringify(error);
        } else {
            errorMessage = String(error);
        }
        
        showError(`Erro ao iniciar geração: ${errorMessage}`);
        resetAppState();
    }
}

/**
 * Iniciar polling do status
 */
function startStatusPolling() {
    if (!appState.currentJobId) return;
    
    appState.pollInterval = setInterval(async () => {
        try {
            await checkJobStatus();
        } catch (error) {
            console.error('Error polling status:', error);
            // Continuar tentando por alguns ciclos
            appState.retryCount++;
            if (appState.retryCount >= MAX_RETRIES) {
                showError('Erro de comunicação com o servidor.');
                resetAppState();
            }
        }
    }, POLL_INTERVAL);
}

/**
 * Verificar status do job
 */
async function checkJobStatus() {
    if (!appState.currentJobId) return;
    
    const status = await makeRequest(`${API_BASE_URL}/status/${appState.currentJobId}`);
    
    // Resetar contador de retry em caso de sucesso
    appState.retryCount = 0;
    
    // Atualizar progresso
    updateProgress(status.progress, status.current_step);
    
    // Verificar status
    switch (status.status) {
        case 'completed':
            handleGenerationComplete(status);
            break;
        case 'error':
            handleGenerationError(status.error_message);
            break;
        case 'running':
        case 'pending':
            // Continuar polling
            break;
        default:
            console.warn('Unknown status:', status.status);
    }
}

/**
 * Lidar com geração completa
 */
function handleGenerationComplete(status) {
    clearInterval(appState.pollInterval);
    appState.pollInterval = null;
    
    // Mostrar seção de resultado
    showSection('result');
    
    // Configurar botão de download
    elements.downloadBtn.onclick = () => downloadVideo(appState.currentJobId);
    
    // Configurar preview do vídeo
    if (status.video_path && appState.currentJobId) {
        const videoPlayer = document.getElementById('video-player');
        const previewUrl = `${API_BASE_URL}/preview/${appState.currentJobId}`;
        
        if (videoPlayer) {
            videoPlayer.src = previewUrl;
            videoPlayer.load(); // Recarregar o player
            
            // Adicionar event listeners para o player
            videoPlayer.addEventListener('loadstart', () => {
                console.log('🎬 Carregando preview do vídeo...');
            });
            
            videoPlayer.addEventListener('canplay', () => {
                console.log('✅ Preview do vídeo carregado com sucesso!');
            });
            
            videoPlayer.addEventListener('error', (e) => {
                console.error('❌ Erro ao carregar preview:', e);
                showToast('Erro ao carregar preview do vídeo', 'warning');
            });
        }
    }
    
    showToast('Vídeo gerado com sucesso!', 'success');
    resetAppState();
}

/**
 * Lidar com erro na geração
 */
function handleGenerationError(errorMessage) {
    clearInterval(appState.pollInterval);
    appState.pollInterval = null;
    
    // Garantir que a mensagem de erro seja uma string legível
    let displayMessage = 'Erro desconhecido na geração do vídeo.';
    
    if (errorMessage) {
        if (typeof errorMessage === 'string') {
            displayMessage = errorMessage;
        } else if (typeof errorMessage === 'object') {
            displayMessage = JSON.stringify(errorMessage);
        } else {
            displayMessage = String(errorMessage);
        }
    }
    
    showError(displayMessage);
    resetAppState();
}

/**
 * Mostrar erro
 */
function showError(message) {
    elements.errorText.textContent = message;
    showSection('error');
    showToast(message, 'error');
}

/**
 * Download do vídeo
 */
function downloadVideo(jobId) {
    const downloadUrl = `${API_BASE_URL}/download/${jobId}`;
    
    // Criar link temporário para download
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = `ai_video_${jobId.substring(0, 8)}.mp4`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    showToast('Download iniciado!', 'success');
}

// ===== EFEITOS VISUAIS =====

/**
 * Atualizar descrição do preset de efeitos
 */
function updateEffectsDescription() {
    const effectsPresetSelect = document.getElementById('effects-preset');
    const effectsDescription = document.getElementById('preset-description');
    
    if (!effectsPresetSelect || !effectsDescription) return;
    
    const preset = effectsPresetSelect.value;
    const descriptions = {
        'professional': '<strong>Profissional:</strong> Transições suaves, zoom sutil e correção de cor para um visual polido e profissional.',
        'cinematic': '<strong>Cinematográfico:</strong> Efeitos dramáticos com transições cinematográficas e correção de cor avançada.',
        'dynamic': '<strong>Dinâmico:</strong> Transições rápidas e efeitos vibrantes para conteúdo energético e envolvente.',
        'subtle': '<strong>Sutil:</strong> Efeitos minimalistas com transições discretas para um visual limpo.',
        'none': '<strong>Sem Efeitos:</strong> Apenas cortes simples entre as cenas, sem efeitos visuais.'
    };
    
    effectsDescription.innerHTML = descriptions[preset] || descriptions['professional'];
}

// Variável global para armazenar os presets carregados
let imagePresetsData = {};

// Função para carregar presets da API
async function loadImagePresets() {
    try {
        const response = await makeRequest(`${API_BASE_URL}/image-presets`);
        
        if (response.success) {
            imagePresetsData = response.presets;
            updateImagePresetSelect();
        } else {
            console.error('Erro ao carregar presets:', response.error);
            // Fallback para presets estáticos
            loadFallbackPresets();
        }
    } catch (error) {
        console.error('Erro na requisição de presets:', error);
        // Fallback para presets estáticos
        loadFallbackPresets();
    }
}

// Função de fallback com presets estáticos
function loadFallbackPresets() {
    imagePresetsData = {
        '3d_cartoon': {
            name: '3D Cartoon',
            description: 'Estilo 3D vibrante inspirado em Pixar e Fortnite, com cores saturadas e personagens estilizados.'
        },
        'realistic': {
            name: 'Realista',
            description: 'Imagens fotorrealistas com alta qualidade e detalhamento natural.'
        },
        'anime': {
            name: 'Anime',
            description: 'Estilo de animação japonesa com traços característicos e cores vibrantes.'
        },
        'digital_art': {
            name: 'Arte Digital',
            description: 'Estilo artístico digital moderno com técnicas de pintura digital.'
        }
    };
    updateImagePresetSelect();
}

// Função para atualizar o select com os presets carregados
function updateImagePresetSelect() {
    const selectElement = document.getElementById('image-preset');
    if (!selectElement) return;
    
    // Limpar opções existentes (exceto a primeira)
    while (selectElement.children.length > 1) {
        selectElement.removeChild(selectElement.lastChild);
    }
    
    // Adicionar opções dos presets carregados
    Object.entries(imagePresetsData).forEach(([key, preset]) => {
        const option = document.createElement('option');
        option.value = key;
        option.textContent = preset.name;
        selectElement.appendChild(option);
    });
}

/**
 * Atualizar descrição do preset de imagem
 */
function updateImagePresetDescription() {
    const imagePreset = document.getElementById('image-preset')?.value;
    const descriptionElement = document.getElementById('image-preset-description');
    
    if (!descriptionElement) return;
    
    let description = '';
    
    if (imagePreset && imagePresetsData[imagePreset]) {
        const preset = imagePresetsData[imagePreset];
        description = `<strong>${preset.name}:</strong> ${preset.description}`;
    } else {
        description = '<strong>Padrão:</strong> Sem estilo específico aplicado. As imagens serão geradas com base apenas nos prompts fornecidos.';
    }
    
    descriptionElement.innerHTML = description;
}



// ===== EVENT LISTENERS =====

/**
 * Configurar event listeners
 */
function setupEventListeners() {
    // Formulário
    elements.form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        if (!validateForm()) return;
        
        // Verificar saúde da API
        const apiHealthy = await checkApiHealth();
        if (!apiHealthy) return;
        
        const formData = getFormData();
        await startVideoGeneration(formData);
    });
    
    // Contadores de caracteres
    if (elements.scriptInput) {
        elements.scriptInput.addEventListener('input', updateScriptCount);
    }
    if (elements.imagePromptsInput) {
        elements.imagePromptsInput.addEventListener('input', updatePromptsCount);
    }
    
    // Botão novo vídeo
    elements.newVideoBtn.addEventListener('click', () => {
        showSection('generation');
        if (elements.scriptInput) {
            elements.scriptInput.focus();
        }
    });
    
    // Botão retry
    elements.retryBtn.addEventListener('click', async () => {
        if (appState.lastFormData) {
            await startVideoGeneration(appState.lastFormData);
        } else {
            showSection('generation');
        }
    });
    
    // Toast close
    elements.toastClose.addEventListener('click', hideToast);
    
    // Auto-hide toast ao clicar
    elements.toast.addEventListener('click', hideToast);
    
    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        // ESC para fechar toast
        if (e.key === 'Escape') {
            hideToast();
        }
        
        // Ctrl+Enter para submeter formulário
        if (e.ctrlKey && e.key === 'Enter' && !appState.isGenerating) {
            elements.form.dispatchEvent(new Event('submit'));
        }
    });
    
    // Prevenir submit duplo
    elements.generateBtn.addEventListener('click', (e) => {
        if (appState.isGenerating) {
            e.preventDefault();
            showToast('Geração já em andamento...', 'warning');
        }
    });
    
    // Effects preset change
    const effectsPresetSelect = document.getElementById('effects-preset');
    if (effectsPresetSelect) {
        effectsPresetSelect.addEventListener('change', updateEffectsDescription);
    }
    
    // Image preset change
    const imagePresetSelect = document.getElementById('image-preset');
    if (imagePresetSelect) {
        imagePresetSelect.addEventListener('change', updateImagePresetDescription);
    }
    
    // Histórico - Botão toggle
    const toggleHistoryBtn = document.getElementById('toggle-history-btn');
    if (toggleHistoryBtn) {
        toggleHistoryBtn.addEventListener('click', toggleHistory);
    }
    
    // Histórico - Botão limpar
    const clearHistoryBtn = document.getElementById('clear-history-btn');
    if (clearHistoryBtn) {
        clearHistoryBtn.addEventListener('click', clearHistory);
    }
    
    // API Key - Event listeners
    if (elements.apiKeyToggle) {
        elements.apiKeyToggle.addEventListener('click', toggleApiKeyVisibility);
    }
    
    if (elements.testApiKeyBtn) {
        elements.testApiKeyBtn.addEventListener('click', () => {
            const apiKey = elements.apiKeyInput ? elements.apiKeyInput.value.trim() : '';
            testApiKey(apiKey);
        });
    }
    
    if (elements.apiKeyInput) {
        // Salvar API key quando sair do campo
        elements.apiKeyInput.addEventListener('blur', () => {
            const apiKey = elements.apiKeyInput.value.trim();
            if (apiKey) {
                saveApiKey(apiKey);
            }
        });
        
        // Permitir Enter para testar conexão
        elements.apiKeyInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                testApiKey(elements.apiKeyInput.value.trim());
            }
        });
    }
    
    // Modal - Event listeners
    if (elements.modalCloseBtn) {
        elements.modalCloseBtn.addEventListener('click', hideApiKeyModal);
    }
    
    if (elements.saveApiKeyBtn) {
        elements.saveApiKeyBtn.addEventListener('click', saveApiKeyFromModal);
    }
    
    if (elements.modalApiKeyInput) {
        elements.modalApiKeyInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                saveApiKeyFromModal();
            }
        });
    }
    
    // Fechar modal clicando no overlay
    if (elements.apiKeyModal) {
        elements.apiKeyModal.addEventListener('click', (e) => {
            if (e.target === elements.apiKeyModal) {
                hideApiKeyModal();
            }
        });
    }
}

// ===== INICIALIZAÇÃO =====

/**
 * Inicializar aplicação
 */
async function initApp() {
    console.log('🚀 Inicializando AI Video GPT Frontend...');
    
    // Configurar event listeners
    setupEventListeners();
    
    // Atualizar contadores iniciais
    updateScriptCount();
    updatePromptsCount();
    
    // Atualizar descrições iniciais
    updateEffectsDescription();
    updateImagePresetDescription();
    
    // Inicializar histórico
    updateHistoryDisplay();
    
    // Inicializar sistema de autenticação
    console.log('🔐 Inicializando sistema de autenticação...');
    
    // Verificar se autenticação é necessária
    await checkAuthRequirement();
    
    // Carregar API key salva
    const savedApiKey = loadApiKey();
    if (savedApiKey) {
        updateApiStatus('disconnected', '🟡 Carregada, não testada');
    }
    
    // Verificar saúde da API na inicialização
    checkApiHealth();
    
    // Se autenticação for necessária e houver API key, testar automaticamente
    if (appState.authRequired && savedApiKey) {
        console.log('🔍 Testando API key salva...');
        await testApiKey(savedApiKey);
    }
    
    // Carregar presets de imagem (após verificação de autenticação)
    loadImagePresets();
    
    // Focar no campo apropriado
    if (appState.authRequired && !appState.apiKey) {
        // Se autenticação necessária e sem API key, focar no campo de API key
        if (elements.apiKeyInput) {
            elements.apiKeyInput.focus();
        }
    } else {
        // Caso contrário, focar no campo de script
        if (elements.scriptInput) {
            elements.scriptInput.focus();
        }
    }
    
    console.log('✅ Frontend inicializado com sucesso!');
    console.log(`🔐 Autenticação ${appState.authRequired ? 'HABILITADA' : 'DESABILITADA'}`);
}

// ===== AUTO-INICIALIZAÇÃO =====

// Aguardar DOM estar pronto
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initApp);
} else {
    initApp();
}

// ===== TRATAMENTO DE ERROS GLOBAIS =====

// Capturar erros não tratados
window.addEventListener('error', (e) => {
    console.error('Unhandled error:', e.error);
    showToast('Ocorreu um erro inesperado.', 'error');
});

// Capturar promises rejeitadas
window.addEventListener('unhandledrejection', (e) => {
    console.error('Unhandled promise rejection:', e.reason);
    showToast('Erro de comunicação.', 'error');
    e.preventDefault();
});

// ===== UTILITÁRIOS DE DEBUG =====

// Expor algumas funções para debug (apenas em desenvolvimento)
if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    window.aiVideoGPT = {
        appState,
        elements,
        showToast,
        checkApiHealth,
        resetAppState
    };
}