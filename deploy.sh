#!/bin/bash

# Script de Deploy para AI Video GPT
# Este script automatiza o processo de deploy em produção

set -e  # Parar em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para logging
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar se Docker está instalado
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker não está instalado. Por favor, instale o Docker primeiro."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose não está instalado. Por favor, instale o Docker Compose primeiro."
        exit 1
    fi
    
    log_success "Docker e Docker Compose estão instalados."
}

# Verificar variáveis de ambiente
check_env() {
    if [ ! -f ".env" ]; then
        log_warning "Arquivo .env não encontrado. Copiando .env.example..."
        cp .env.example .env
        log_warning "Por favor, configure as variáveis de ambiente no arquivo .env antes de continuar."
        log_warning "Especialmente: GEMINI_API_KEY, ELEVENLABS_API_KEY, SECRET_KEY, API_KEY"
        read -p "Pressione Enter após configurar o arquivo .env..."
    fi
    
    # Verificar se as variáveis críticas estão definidas
    source .env
    
    if [ "$GEMINI_API_KEY" = "sua_api_key_aqui" ] || [ -z "$GEMINI_API_KEY" ]; then
        log_error "GEMINI_API_KEY não está configurada corretamente no arquivo .env"
        exit 1
    fi
    
    if [ "$SECRET_KEY" = "change-this-secret-key-in-production" ] || [ -z "$SECRET_KEY" ]; then
        log_error "SECRET_KEY deve ser alterada para produção no arquivo .env"
        exit 1
    fi
    
    log_success "Variáveis de ambiente verificadas."
}

# Criar diretórios necessários
setup_directories() {
    log "Criando diretórios necessários..."
    
    mkdir -p outputs/videos
    mkdir -p outputs/audio
    mkdir -p outputs/images
    mkdir -p logs
    mkdir -p ssl
    
    # Ajustar permissões
    chmod 755 outputs
    chmod 755 logs
    
    log_success "Diretórios criados com sucesso."
}

# Build das imagens Docker
build_images() {
    log "Construindo imagens Docker..."
    
    docker-compose build --no-cache
    
    log_success "Imagens Docker construídas com sucesso."
}

# Iniciar serviços
start_services() {
    log "Iniciando serviços..."
    
    # Parar serviços existentes
    docker-compose down
    
    # Iniciar Redis primeiro
    log "Iniciando Redis..."
    docker-compose up -d redis
    
    # Aguardar Redis estar pronto
    log "Aguardando Redis estar pronto..."
    sleep 10
    
    # Verificar se Redis está funcionando
    if ! docker-compose exec redis redis-cli ping | grep -q PONG; then
        log_error "Redis não está respondendo corretamente."
        exit 1
    fi
    
    log_success "Redis está funcionando."
    
    # Iniciar aplicação
    log "Iniciando aplicação..."
    docker-compose up -d app
    
    # Aguardar aplicação estar pronta
    log "Aguardando aplicação estar pronta..."
    sleep 15
    
    # Verificar health da aplicação
    for i in {1..30}; do
        if curl -f http://localhost:5000/health &> /dev/null; then
            log_success "Aplicação está funcionando."
            break
        fi
        
        if [ $i -eq 30 ]; then
            log_error "Aplicação não está respondendo após 30 tentativas."
            docker-compose logs app
            exit 1
        fi
        
        log "Tentativa $i/30 - Aguardando aplicação..."
        sleep 2
    done
    
    # Iniciar workers
    log "Iniciando workers..."
    docker-compose up -d worker
    
    log_success "Todos os serviços foram iniciados com sucesso."
}

# Verificar status dos serviços
check_services() {
    log "Verificando status dos serviços..."
    
    # Verificar containers
    echo "\n=== Status dos Containers ==="
    docker-compose ps
    
    # Verificar health da aplicação
    echo "\n=== Health Check da Aplicação ==="
    curl -s http://localhost:5000/health | python -m json.tool || log_error "Falha no health check"
    
    # Verificar logs recentes
    echo "\n=== Logs Recentes ==="
    docker-compose logs --tail=10 app
    
    log_success "Verificação de status concluída."
}

# Função principal
main() {
    log "Iniciando deploy do AI Video GPT..."
    
    # Verificações pré-deploy
    check_docker
    check_env
    
    # Setup
    setup_directories
    
    # Build e deploy
    build_images
    start_services
    
    # Verificações pós-deploy
    check_services
    
    echo "\n${GREEN}========================================${NC}"
    echo "${GREEN}🎉 Deploy concluído com sucesso! 🎉${NC}"
    echo "${GREEN}========================================${NC}"
    echo ""
    echo "📱 Aplicação: http://localhost:5000"
    echo "🔍 Health Check: http://localhost:5000/health"
    echo "📊 Logs: docker-compose logs -f"
    echo ""
    echo "Para parar os serviços: docker-compose down"
    echo "Para ver logs: docker-compose logs -f [service_name]"
    echo ""
}

# Verificar argumentos
case "${1:-}" in
    "check")
        check_services
        ;;
    "stop")
        log "Parando serviços..."
        docker-compose down
        log_success "Serviços parados."
        ;;
    "restart")
        log "Reiniciando serviços..."
        docker-compose restart
        log_success "Serviços reiniciados."
        ;;
    "logs")
        docker-compose logs -f
        ;;
    "clean")
        log "Limpando containers e imagens..."
        docker-compose down -v
        docker system prune -f
        log_success "Limpeza concluída."
        ;;
    "")
        main
        ;;
    *)
        echo "Uso: $0 [check|stop|restart|logs|clean]"
        echo ""
        echo "Comandos disponíveis:"
        echo "  (nenhum)  - Deploy completo"
        echo "  check     - Verificar status dos serviços"
        echo "  stop      - Parar todos os serviços"
        echo "  restart   - Reiniciar todos os serviços"
        echo "  logs      - Mostrar logs em tempo real"
        echo "  clean     - Limpar containers e imagens"
        exit 1
        ;;
esac