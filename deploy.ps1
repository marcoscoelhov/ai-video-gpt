# Script de Deploy para AI Video GPT (Windows PowerShell)
# Este script automatiza o processo de deploy em produção no Windows

param(
    [Parameter(Position=0)]
    [ValidateSet('', 'check', 'stop', 'restart', 'logs', 'clean')]
    [string]$Action = ''
)

# Configurações
$ErrorActionPreference = 'Stop'

# Funções de logging com cores
function Write-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$timestamp] $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Verificar se Docker está instalado
function Test-Docker {
    Write-Log "Verificando instalação do Docker..."
    
    try {
        $dockerVersion = docker --version
        Write-Success "Docker encontrado: $dockerVersion"
    }
    catch {
        Write-Error "Docker não está instalado. Por favor, instale o Docker Desktop primeiro."
        exit 1
    }
    
    try {
        $composeVersion = docker-compose --version
        Write-Success "Docker Compose encontrado: $composeVersion"
    }
    catch {
        Write-Error "Docker Compose não está instalado. Por favor, instale o Docker Compose primeiro."
        exit 1
    }
}

# Verificar variáveis de ambiente
function Test-Environment {
    Write-Log "Verificando configurações de ambiente..."
    
    if (-not (Test-Path ".env")) {
        Write-Warning "Arquivo .env não encontrado. Copiando .env.example..."
        Copy-Item ".env.example" ".env"
        Write-Warning "Por favor, configure as variáveis de ambiente no arquivo .env antes de continuar."
        Write-Warning "Especialmente: GEMINI_API_KEY, ELEVENLABS_API_KEY, SECRET_KEY, API_KEY"
        Read-Host "Pressione Enter após configurar o arquivo .env"
    }
    
    # Ler arquivo .env
    $envVars = @{}
    Get-Content ".env" | ForEach-Object {
        if ($_ -match '^([^=]+)=(.*)$') {
            $envVars[$matches[1]] = $matches[2]
        }
    }
    
    # Verificar variáveis críticas
    if ($envVars['GEMINI_API_KEY'] -eq 'sua_api_key_aqui' -or [string]::IsNullOrEmpty($envVars['GEMINI_API_KEY'])) {
        Write-Error "GEMINI_API_KEY não está configurada corretamente no arquivo .env"
        exit 1
    }
    
    if ($envVars['SECRET_KEY'] -eq 'change-this-secret-key-in-production' -or [string]::IsNullOrEmpty($envVars['SECRET_KEY'])) {
        Write-Error "SECRET_KEY deve ser alterada para produção no arquivo .env"
        exit 1
    }
    
    Write-Success "Variáveis de ambiente verificadas."
}

# Criar diretórios necessários
function New-Directories {
    Write-Log "Criando diretórios necessários..."
    
    $directories = @(
        "outputs\videos",
        "outputs\audio", 
        "outputs\images",
        "logs",
        "ssl"
    )
    
    foreach ($dir in $directories) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
        }
    }
    
    Write-Success "Diretórios criados com sucesso."
}

# Build das imagens Docker
function Build-Images {
    Write-Log "Construindo imagens Docker..."
    
    try {
        docker-compose build --no-cache
        Write-Success "Imagens Docker construídas com sucesso."
    }
    catch {
        Write-Error "Falha ao construir imagens Docker: $_"
        exit 1
    }
}

# Iniciar serviços
function Start-Services {
    Write-Log "Iniciando serviços..."
    
    # Parar serviços existentes
    try {
        docker-compose down
    }
    catch {
        Write-Warning "Nenhum serviço anterior para parar."
    }
    
    # Iniciar Redis primeiro
    Write-Log "Iniciando Redis..."
    docker-compose up -d redis
    
    # Aguardar Redis estar pronto
    Write-Log "Aguardando Redis estar pronto..."
    Start-Sleep -Seconds 10
    
    # Verificar se Redis está funcionando
    try {
        $redisPing = docker-compose exec -T redis redis-cli ping
        if ($redisPing -notmatch "PONG") {
            throw "Redis não está respondendo corretamente."
        }
        Write-Success "Redis está funcionando."
    }
    catch {
        Write-Error "Redis não está respondendo corretamente."
        exit 1
    }
    
    # Iniciar aplicação
    Write-Log "Iniciando aplicação..."
    docker-compose up -d app
    
    # Aguardar aplicação estar pronta
    Write-Log "Aguardando aplicação estar pronta..."
    Start-Sleep -Seconds 15
    
    # Verificar health da aplicação
    $maxAttempts = 30
    for ($i = 1; $i -le $maxAttempts; $i++) {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:5000/health" -UseBasicParsing -TimeoutSec 5
            if ($response.StatusCode -eq 200) {
                Write-Success "Aplicação está funcionando."
                break
            }
        }
        catch {
            if ($i -eq $maxAttempts) {
                Write-Error "Aplicação não está respondendo após $maxAttempts tentativas."
                docker-compose logs app
                exit 1
            }
            
            Write-Log "Tentativa $i/$maxAttempts - Aguardando aplicação..."
            Start-Sleep -Seconds 2
        }
    }
    
    # Iniciar workers
    Write-Log "Iniciando workers..."
    docker-compose up -d worker
    
    Write-Success "Todos os serviços foram iniciados com sucesso."
}

# Verificar status dos serviços
function Test-Services {
    Write-Log "Verificando status dos serviços..."
    
    # Verificar containers
    Write-Host "`n=== Status dos Containers ===" -ForegroundColor Cyan
    docker-compose ps
    
    # Verificar health da aplicação
    Write-Host "`n=== Health Check da Aplicação ===" -ForegroundColor Cyan
    try {
        $healthResponse = Invoke-WebRequest -Uri "http://localhost:5000/health" -UseBasicParsing
        $healthResponse.Content | ConvertFrom-Json | ConvertTo-Json -Depth 10
    }
    catch {
        Write-Error "Falha no health check: $_"
    }
    
    # Verificar logs recentes
    Write-Host "`n=== Logs Recentes ===" -ForegroundColor Cyan
    docker-compose logs --tail=10 app
    
    Write-Success "Verificação de status concluída."
}

# Função principal
function Start-Deploy {
    Write-Log "Iniciando deploy do AI Video GPT..."
    
    # Verificações pré-deploy
    Test-Docker
    Test-Environment
    
    # Setup
    New-Directories
    
    # Build e deploy
    Build-Images
    Start-Services
    
    # Verificações pós-deploy
    Test-Services
    
    Write-Host "`n========================================" -ForegroundColor Green
    Write-Host "🎉 Deploy concluído com sucesso! 🎉" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "📱 Aplicação: http://localhost:5000" -ForegroundColor White
    Write-Host "🔍 Health Check: http://localhost:5000/health" -ForegroundColor White
    Write-Host "📊 Logs: docker-compose logs -f" -ForegroundColor White
    Write-Host ""
    Write-Host "Para parar os serviços: docker-compose down" -ForegroundColor Yellow
    Write-Host "Para ver logs: docker-compose logs -f [service_name]" -ForegroundColor Yellow
    Write-Host ""
}

# Processar argumentos
switch ($Action) {
    'check' {
        Test-Services
    }
    'stop' {
        Write-Log "Parando serviços..."
        docker-compose down
        Write-Success "Serviços parados."
    }
    'restart' {
        Write-Log "Reiniciando serviços..."
        docker-compose restart
        Write-Success "Serviços reiniciados."
    }
    'logs' {
        docker-compose logs -f
    }
    'clean' {
        Write-Log "Limpando containers e imagens..."
        docker-compose down -v
        docker system prune -f
        Write-Success "Limpeza concluída."
    }
    '' {
        Start-Deploy
    }
    default {
        Write-Host "Uso: .\deploy.ps1 [check|stop|restart|logs|clean]" -ForegroundColor White
        Write-Host ""
        Write-Host "Comandos disponíveis:" -ForegroundColor White
        Write-Host "  (nenhum)  - Deploy completo" -ForegroundColor Gray
        Write-Host "  check     - Verificar status dos serviços" -ForegroundColor Gray
        Write-Host "  stop      - Parar todos os serviços" -ForegroundColor Gray
        Write-Host "  restart   - Reiniciar todos os serviços" -ForegroundColor Gray
        Write-Host "  logs      - Mostrar logs em tempo real" -ForegroundColor Gray
        Write-Host "  clean     - Limpar containers e imagens" -ForegroundColor Gray
        exit 1
    }
}