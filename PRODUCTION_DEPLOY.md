# 🚀 Guia de Deploy em Produção - AI Video GPT

Este guia fornece instruções completas para fazer o deploy da aplicação AI Video GPT em ambiente de produção usando Docker.

## 📋 Pré-requisitos

### Requisitos do Sistema
- **Docker**: Versão 20.10 ou superior
- **Docker Compose**: Versão 2.0 ou superior
- **Sistema Operacional**: Linux, macOS ou Windows
- **RAM**: Mínimo 4GB, recomendado 8GB
- **Armazenamento**: Mínimo 10GB livres
- **CPU**: 2 cores, recomendado 4 cores

### APIs Necessárias
- **Google Gemini API Key**: Para geração de conteúdo
- **ElevenLabs API Key**: Para síntese de voz (opcional)

## 🔧 Configuração Inicial

### 1. Clonar o Repositório
```bash
git clone <seu-repositorio>
cd ai-video-gpt
```

### 2. Configurar Variáveis de Ambiente
```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar configurações
nano .env  # ou seu editor preferido
```

#### Variáveis Obrigatórias
```env
# APIs
GEMINI_API_KEY=sua_chave_gemini_aqui
ELEVENLABS_API_KEY=sua_chave_elevenlabs_aqui

# Segurança
SECRET_KEY=uma_chave_secreta_muito_forte_e_unica
API_KEY=sua_api_key_personalizada
REQUIRE_API_KEY=true

# Ambiente
ENVIRONMENT=production
```

#### Variáveis Opcionais
```env
# Redis
REDIS_URL=redis://redis:6379/0
RATELIMIT_STORAGE_URL=redis://redis:6379/1

# Rate Limiting
DEFAULT_RATE_LIMIT_PER_HOUR=100
DEFAULT_RATE_LIMIT_PER_MINUTE=20

# Workers
WORKER_COUNT=2

# Monitoramento
DISK_USAGE_THRESHOLD=90
MEMORY_USAGE_THRESHOLD=85
```

## 🚀 Deploy Automático

### Linux/macOS
```bash
# Tornar script executável
chmod +x deploy.sh

# Executar deploy
./deploy.sh
```

### Windows (PowerShell)
```powershell
# Executar como Administrador
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Executar deploy
.\deploy.ps1
```

## 🔧 Deploy Manual

### 1. Construir Imagens
```bash
docker-compose build --no-cache
```

### 2. Iniciar Serviços
```bash
# Iniciar Redis
docker-compose up -d redis

# Aguardar Redis estar pronto
sleep 10

# Iniciar aplicação
docker-compose up -d app

# Iniciar workers
docker-compose up -d worker
```

### 3. Verificar Status
```bash
# Status dos containers
docker-compose ps

# Health check
curl http://localhost:5000/health

# Logs
docker-compose logs -f
```

## 🏗️ Arquitetura de Produção

### Serviços
- **app**: Aplicação Flask principal (porta 5000)
- **redis**: Cache e sistema de filas (porta 6379)
- **worker**: Processamento assíncrono de vídeos
- **nginx**: Proxy reverso (porta 80/443) - opcional

### Volumes
- `./outputs`: Arquivos gerados (vídeos, áudio, imagens)
- `./logs`: Logs da aplicação
- `redis_data`: Dados persistentes do Redis

### Rede
- Rede interna `ai-video-network` para comunicação entre serviços

## 🔒 Configurações de Segurança

### Headers de Segurança
- X-Frame-Options: DENY
- X-Content-Type-Options: nosniff
- X-XSS-Protection: 1; mode=block
- Content-Security-Policy configurado

### Rate Limiting
- API geral: 100 req/hora, 20 req/minuto
- Geração de vídeo: 5 req/minuto
- Downloads: 10 req/minuto

### Autenticação
- API Key obrigatória em produção
- Verificação via header, query param ou body

## 📊 Monitoramento

### Health Check
```bash
curl http://localhost:5000/health
```

Retorna:
- Status da aplicação
- Status do Redis
- Uso de disco e memória
- Tamanho da fila

### Logs
```bash
# Todos os serviços
docker-compose logs -f

# Serviço específico
docker-compose logs -f app
docker-compose logs -f worker
docker-compose logs -f redis
```

### Métricas
- **Healthy**: Todos os sistemas funcionando
- **Degraded**: Alguns problemas detectados
- **Unhealthy**: Problemas críticos

## 🔧 Comandos de Gerenciamento

### Scripts de Deploy
```bash
# Deploy completo
./deploy.sh

# Verificar status
./deploy.sh check

# Parar serviços
./deploy.sh stop

# Reiniciar serviços
./deploy.sh restart

# Ver logs
./deploy.sh logs

# Limpeza completa
./deploy.sh clean
```

### Docker Compose
```bash
# Iniciar todos os serviços
docker-compose up -d

# Parar todos os serviços
docker-compose down

# Reiniciar serviço específico
docker-compose restart app

# Escalar workers
docker-compose up -d --scale worker=4

# Ver logs em tempo real
docker-compose logs -f app

# Executar comando em container
docker-compose exec app python -c "print('Hello')"
```

## 🔄 Backup e Restauração

### Backup
```bash
# Backup dos dados do Redis
docker-compose exec redis redis-cli BGSAVE
docker cp $(docker-compose ps -q redis):/data/dump.rdb ./backup/

# Backup dos outputs
tar -czf backup/outputs_$(date +%Y%m%d_%H%M%S).tar.gz outputs/

# Backup dos logs
tar -czf backup/logs_$(date +%Y%m%d_%H%M%S).tar.gz logs/
```

### Restauração
```bash
# Parar serviços
docker-compose down

# Restaurar dados do Redis
docker cp ./backup/dump.rdb $(docker-compose ps -q redis):/data/

# Restaurar outputs
tar -xzf backup/outputs_YYYYMMDD_HHMMSS.tar.gz

# Reiniciar serviços
docker-compose up -d
```

## 🚨 Troubleshooting

### Problemas Comuns

#### 1. Redis não conecta
```bash
# Verificar se Redis está rodando
docker-compose ps redis

# Verificar logs do Redis
docker-compose logs redis

# Testar conexão
docker-compose exec redis redis-cli ping
```

#### 2. Aplicação não responde
```bash
# Verificar logs da aplicação
docker-compose logs app

# Verificar health check
curl -v http://localhost:5000/health

# Reiniciar aplicação
docker-compose restart app
```

#### 3. Workers não processam
```bash
# Verificar logs dos workers
docker-compose logs worker

# Verificar fila do Redis
docker-compose exec redis redis-cli LLEN video_generation

# Reiniciar workers
docker-compose restart worker
```

#### 4. Erro de permissões
```bash
# Ajustar permissões dos diretórios
sudo chown -R $USER:$USER outputs/ logs/
chmod -R 755 outputs/ logs/
```

#### 5. Falta de espaço em disco
```bash
# Limpar containers antigos
docker system prune -f

# Limpar volumes não utilizados
docker volume prune -f

# Limpar outputs antigos
find outputs/ -type f -mtime +7 -delete
```

### Logs de Debug
```bash
# Habilitar logs detalhados
export LOG_LEVEL=DEBUG
docker-compose restart app worker

# Verificar logs detalhados
docker-compose logs -f app | grep DEBUG
```

## 🔧 Configurações Avançadas

### Nginx (Proxy Reverso)
```bash
# Habilitar Nginx
docker-compose --profile production up -d nginx
```

### SSL/HTTPS
1. Colocar certificados em `./ssl/`
2. Descomentar configuração HTTPS no `nginx.conf`
3. Reiniciar Nginx

### Escalabilidade
```bash
# Múltiplos workers
docker-compose up -d --scale worker=4

# Load balancer (adicionar ao docker-compose.yml)
# Configurar múltiplas instâncias da app
```

## 📈 Otimizações de Performance

### Redis
- Configurar `maxmemory` adequadamente
- Usar `allkeys-lru` para eviction policy
- Habilitar persistência com `appendonly yes`

### Aplicação
- Ajustar número de workers baseado na CPU
- Configurar timeouts adequados
- Implementar cache de resultados

### Sistema
- Usar SSD para armazenamento
- Configurar swap adequadamente
- Monitorar uso de recursos

## 📞 Suporte

Para problemas ou dúvidas:
1. Verificar logs detalhados
2. Consultar seção de troubleshooting
3. Verificar issues no repositório
4. Contatar equipe de desenvolvimento

---

**Nota**: Este guia assume conhecimento básico de Docker e administração de sistemas. Para ambientes de produção críticos, considere consultar um especialista em DevOps.