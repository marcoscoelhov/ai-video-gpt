# AI Video GPT - Documentação da API

## Visão Geral

A API do AI Video GPT permite gerar vídeos automaticamente a partir de scripts de texto, com suporte a diferentes vozes, efeitos visuais e presets de imagem.

## Autenticação

A API utiliza autenticação via API Key. A chave deve ser fornecida em uma das seguintes formas:

- **Header HTTP**: `X-API-Key: sua-api-key`
- **Query Parameter**: `?api_key=sua-api-key`
- **Request Body**: `{"api_key": "sua-api-key"}`

### Configuração de Autenticação

```bash
# Habilitar autenticação (padrão)
export REQUIRE_API_KEY=true
export API_KEY=sua-chave-secreta

# Desabilitar autenticação (apenas desenvolvimento)
export REQUIRE_API_KEY=false
```

## Base URL

```
http://localhost:5000
```

## Endpoints

### 1. Verificação de Saúde

#### `GET /api/health`

Verifica o status da API e serviços conectados.

**Resposta:**
```json
{
  "status": "healthy",
  "message": "AI Video GPT API está funcionando",
  "timestamp": "2025-01-27T10:00:00",
  "authentication_required": true,
  "version": "1.0.0",
  "environment": "development",
  "services": {
    "redis": {
      "status": "connected",
      "ping_time_ms": 2.5
    },
    "queue": {
      "status": "active",
      "pending_jobs": 0
    }
  }
}
```

### 2. Informações de Autenticação

#### `GET /api/auth/info`

Retorna informações sobre os métodos de autenticação (endpoint público).

**Resposta:**
```json
{
  "authentication_required": true,
  "api_key_methods": [
    "Header: X-API-Key",
    "Query parameter: api_key",
    "Request body: api_key"
  ],
  "message": "AI Video GPT API - Autenticação via API Key"
}
```

### 3. Validar API Key

#### `POST /api/auth/validate` 🔒

Valida se a API key fornecida é válida.

**Headers:**
```
X-API-Key: sua-api-key
```

**Resposta:**
```json
{
  "valid": true,
  "message": "API key válida",
  "authenticated": true
}
```

### 4. Gerar Vídeo

#### `POST /api/generate-video` 🔒

Inicia a geração de um novo vídeo.

**Headers:**
```
Content-Type: application/json
X-API-Key: sua-api-key
```

**Request Body:**
```json
{
  "script": "Bem-vindos ao futuro da inteligência artificial. Hoje vamos explorar como a IA está transformando o mundo.",
  "image_prompts": [
    "Futuristic cityscape with AI technology",
    "Robot and human working together",
    "Digital brain with neural networks"
  ],
  "voice_provider": "auto",
  "voice_type": "narrator",
  "language": "pt",
  "video_format": "standard",
  "effects_preset": "professional",
  "enable_effects": true,
  "image_preset": "cinematic"
}
```

**Parâmetros:**

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|----------|
| `script` | string | ✅ | Texto do roteiro do vídeo |
| `image_prompts` | array | ✅ | Lista de prompts para geração de imagens |
| `voice_provider` | string | ❌ | Provedor de voz (auto, elevenlabs) |
| `voice_type` | string | ❌ | Tipo de voz (narrator, casual, professional) |
| `language` | string | ❌ | Idioma (pt, en, es) |
| `video_format` | string | ❌ | Formato do vídeo (standard, widescreen) |
| `effects_preset` | string | ❌ | Preset de efeitos (subtle, professional, dynamic) |
| `enable_effects` | boolean | ❌ | Habilitar efeitos visuais |
| `image_preset` | string | ❌ | Preset de estilo de imagem |

**Resposta:**
```json
{
  "success": true,
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Vídeo adicionado à fila de processamento",
  "estimated_time_minutes": 5,
  "status_url": "/api/status/550e8400-e29b-41d4-a716-446655440000"
}
```

### 5. Status do Job

#### `GET /api/status/{job_id}` 🔒

Verifica o status de um job de geração de vídeo.

**Headers:**
```
X-API-Key: sua-api-key
```

**Resposta:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "progress": 65,
  "current_step": "Gerando áudio...",
  "created_at": "2025-01-27T10:00:00",
  "updated_at": "2025-01-27T10:03:00",
  "estimated_completion": "2025-01-27T10:05:00"
}
```

**Status possíveis:**
- `pending`: Job na fila
- `processing`: Em processamento
- `completed`: Concluído com sucesso
- `failed`: Falhou
- `cancelled`: Cancelado

### 6. Download do Vídeo

#### `GET /api/download/{job_id}` 🔒

Faz download do vídeo gerado.

**Headers:**
```
X-API-Key: sua-api-key
```

**Resposta:**
- **Content-Type**: `video/mp4`
- **Content-Disposition**: `attachment; filename="video_{job_id}.mp4"`

### 7. Preview do Vídeo

#### `GET /api/preview/{job_id}` 🔒

Visualiza o vídeo no navegador (streaming).

**Headers:**
```
X-API-Key: sua-api-key
```

**Resposta:**
- **Content-Type**: `video/mp4`
- Streaming do arquivo de vídeo

### 8. Listar Jobs

#### `GET /api/jobs` 🔒

Lista todos os jobs com paginação.

**Headers:**
```
X-API-Key: sua-api-key
```

**Query Parameters:**
- `page`: Número da página (padrão: 1)
- `per_page`: Items por página (padrão: 20, máximo: 100)
- `status`: Filtrar por status

**Resposta:**
```json
{
  "jobs": [
    {
      "job_id": "550e8400-e29b-41d4-a716