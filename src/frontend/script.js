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

// ===== ELEMENTOS DO DOM =====
const elements = {
    // Formulário
    form: document.getElementById('video-form'),
    scriptInput: document.getElementById('script'),
    imagePromptsInput: document.getElementById('image-prompts'),
    generateBtn: document.getElementById('generate-btn'),
    charCount: document.getElementById('char-count'),
    
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
    lastFormData: null
};

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
 * Fazer requisição HTTP com tratamento de erro
 */
async function makeRequest(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || `HTTP ${response.status}`);
        }
        
        return data;
    } catch (error) {
        console.error('Request failed:', error);
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
    return {
        script: elements.scriptInput.value.trim(),
        image_prompts: elements.imagePromptsInput.value.trim(),
        voice_provider: 'elevenlabs',  // Valor padrão
        voice_type: 'narrator',       // Valor padrão
        language: 'pt',               // Valor padrão
        video_format: 'tiktok'        // Valor padrão
    };
}

/**
 * Atualizar contador de caracteres (função mantida para compatibilidade)
 */
function updateCharCount() {
    // Esta função é mantida para compatibilidade, mas agora usa updateScriptCount
    updateScriptCount();
    updatePromptsCount();
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
        
        // Atualizar UI
        elements.generateBtn.disabled = true;
        elements.generateBtn.innerHTML = `
            <span class="btn-icon">⏳</span>
            <span class="btn-text">Iniciando...</span>
        `;
        
        // Fazer requisição para iniciar geração
        const response = await makeRequest(`${API_BASE_URL}/generate-video`, {
            method: 'POST',
            body: JSON.stringify(formData)
        });
        
        appState.currentJobId = response.job_id;
        
        // Mostrar seção de progresso
        showSection('progress');
        updateProgress(5, 'Geração iniciada...');
        
        // Iniciar polling do status
        startStatusPolling();
        
        showToast('Geração de vídeo iniciada com sucesso!', 'success');
        
    } catch (error) {
        console.error('Error starting video generation:', error);
        showError(`Erro ao iniciar geração: ${error.message}`);
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
    
    showError(errorMessage || 'Erro desconhecido na geração do vídeo.');
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
    
    // Script textarea functionality
    const scriptInput = document.getElementById('script');
    if (scriptInput) {
        scriptInput.addEventListener('input', updateScriptCount);
    }
    
    // Image prompts textarea functionality
    const promptsInput = document.getElementById('image-prompts');
    if (promptsInput) {
        promptsInput.addEventListener('input', updatePromptsCount);
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
}

// ===== INICIALIZAÇÃO =====

/**
 * Inicializar aplicação
 */
function initApp() {
    console.log('🚀 Inicializando AI Video GPT Frontend...');
    
    // Configurar event listeners
    setupEventListeners();
    
    // Atualizar contadores iniciais
    updateScriptCount();
    updatePromptsCount();
    
    // Verificar saúde da API na inicialização
    checkApiHealth();
    
    // Focar no campo de script
    if (elements.scriptInput) {
        elements.scriptInput.focus();
    }
    
    console.log('✅ Frontend inicializado com sucesso!');
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