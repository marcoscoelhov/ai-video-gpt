# AI Video GPT

Gerador de vídeos curtos com IA usando Gemini e ElevenLabs.

## Funcionalidades

- 🎬 Geração automática de roteiros
- 🎨 Criação de imagens com IA
- 🎙️ Síntese de voz natural
- 📜 Legendas sincronizadas
- 🎞️ Montagem automática de vídeo

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/ai-video-gpt.git
cd ai-video-gpt
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure as chaves de API no arquivo `.env`:
```
GEMINI_API_KEY=sua_chave_gemini
ELEVENLABS_API_KEY=sua_chave_elevenlabs  # Opcional
```

## 🚀 Como Usar

### Método 1: Interface Web (Recomendado)
1. Execute o servidor Flask:
   ```bash
   python app.py
   ```
2. Abra seu navegador e acesse: `http://localhost:5000`
3. Use a interface web para gerar vídeos facilmente
4. Aguarde a geração completa (pode levar alguns minutos)
5. Faça o download do vídeo quando estiver pronto

### Método 2: Linha de Comando
```bash
# Exemplo básico
python main.py --theme "Um gato astronauta explorando uma estação espacial futurística"

# Com configurações de voz personalizadas
python main.py --theme "Aventura em uma cidade cyberpunk" --voice-provider elevenlabs --voice-type female --language pt-br

# Modo de teste (sem fazer chamadas de API)
python main.py --test
```

### 🔧 Solução de Problemas

**Problema: Vídeo não está sendo criado**
- Verifique se as chaves de API estão configuradas no arquivo `.env`
- Certifique-se de que o FFmpeg está instalado no sistema
- Verifique os logs do servidor para erros específicos

**Problema: Download não funciona**
- Aguarde a geração completa (status: 100%)
- Verifique se o arquivo foi criado na pasta `outputs/videos/`
- Tente acessar o endpoint de preview primeiro: `/api/preview/<job_id>`

## Estrutura do Projeto

```
ai-video-gpt/
├── src/                     # Código fonte principal
│   ├── core/               # Módulos principais
│   │   ├── scriptgen.py    # Geração de roteiros
│   │   ├── imagegen.py     # Geração de imagens
│   │   ├── voice.py        # Síntese de voz
│   │   ├── subtitle.py     # Geração de legendas
│   │   └── assemble.py     # Montagem de vídeo
│   ├── config/             # Configurações e clientes API
│   ├── utils/              # Utilitários e helpers
│   └── frontend/           # Interface web
├── examples/               # Exemplos e demos
│   ├── basic/              # Exemplos básicos
│   └── advanced/           # Exemplos avançados
├── scripts/                # Scripts utilitários
│   ├── demo/               # Scripts de demonstração
│   ├── render/             # Scripts de renderização
│   └── utils/              # Scripts de teste e utilitários
├── tests/                  # Testes automatizados
│   ├── unit/               # Testes unitários
│   ├── integration/        # Testes de integração
│   └── e2e/                # Testes end-to-end
├── output/                 # Arquivos de saída
│   ├── videos/             # Vídeos gerados
│   ├── audio/              # Arquivos de áudio
│   ├── images/             # Imagens geradas
│   └── subtitles/          # Arquivos de legenda
├── temp/                   # Arquivos temporários
├── docs/                   # Documentação
│   ├── api/                # Documentação da API
│   ├── user_guide/         # Guia do usuário
│   └── development/        # Documentação de desenvolvimento
├── main.py                 # Script principal
├── app.py                  # Servidor Flask
└── requirements.txt        # Dependências
```
