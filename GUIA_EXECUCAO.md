# 🎬 Guia de Execução - AI Video GPT

## 📋 Pré-requisitos

✅ **Já configurado:**
- Python 3.12.7 instalado
- Dependências básicas instaladas (`google-generativeai`, `python-dotenv`)
- Estrutura do projeto organizada

## 🔧 Configuração Necessária

### 1. Configurar Chaves de API

O arquivo `.env` foi criado com as variáveis necessárias. Você precisa:

1. **Obter chave do Gemini:**
   - Acesse: https://makersuite.google.com/app/apikey
   - Crie uma conta Google (se necessário)
   - Gere uma nova chave de API

2. **Obter chave do OpenAI:**
   - Acesse: https://platform.openai.com/api-keys
   - Crie uma conta OpenAI (se necessário)
   - Gere uma nova chave de API

3. **Editar o arquivo `.env`:**
   ```bash
   # Substitua pelas suas chaves reais
   GEMINI_API_KEY=sua_chave_gemini_aqui
   OPENAI_API_KEY=sua_chave_openai_aqui
   ```

### 2. Instalar Dependências Completas

```bash
pip install -r requirements.txt
```

**Dependências adicionais que podem ser necessárias:**
```bash
pip install openai pillow moviepy ffmpeg-python
```

### 3. Instalar FFmpeg (para montagem de vídeo)

**Windows:**
- Baixe de: https://ffmpeg.org/download.html
- Ou use chocolatey: `choco install ffmpeg`
- Ou use winget: `winget install ffmpeg`

## 🚀 Como Executar

### Opção 1: Script Principal
```bash
python main.py --theme "Seu tema aqui"
```

### Opção 2: Script de Exemplo (Recomendado)
```bash
python run_example.py
```

### Exemplos de Temas
```bash
python main.py --theme "Cyberpunk city exploration"
python main.py --theme "Medieval fantasy adventure"
python main.py --theme "Space exploration mission"
python main.py --theme "Underwater ocean discovery"
```

## 📁 Estrutura de Saída

O projeto criará a seguinte estrutura na pasta `output/`:

```
output/
└── video_tema_20241220_143022/
    ├── script.json          # Roteiro gerado
    ├── images/             # Imagens geradas
    │   ├── scene_1.png
    │   ├── scene_2.png
    │   └── ...
    ├── audio/              # Áudios gerados
    │   ├── scene_1.wav
    │   ├── scene_2.wav
    │   └── ...
    ├── subtitles/          # Legendas
    │   └── subtitles.srt
    └── video_tema_20241220_143022.mp4  # Vídeo final
```

## 🔍 Verificação de Status

Para verificar se tudo está configurado:

```bash
python run_example.py
```

Este script verificará:
- ✅ Chaves de API configuradas
- ✅ Dependências instaladas
- ✅ Ambiente pronto para execução

## ⚠️ Solução de Problemas

### Erro: "API key not valid"
- Verifique se as chaves no `.env` estão corretas
- Confirme se você tem créditos nas APIs

### Erro: "ModuleNotFoundError"
- Execute: `pip install -r requirements.txt`
- Instale dependências adicionais se necessário

### Erro: "FFmpeg not found"
- Instale FFmpeg no sistema
- Configure o caminho no `.env`: `FFMPEG_PATH=caminho/para/ffmpeg`

## 💰 Custos Estimados

- **Por vídeo:** ~$0.15 USD
- **Gemini API:** Gratuito até 1.000 req/dia
- **OpenAI:** Varia conforme uso de DALL-E e TTS

## 📞 Próximos Passos

1. Configure suas chaves de API no arquivo `.env`
2. Execute `python run_example.py` para testar
3. Se tudo estiver OK, use `python main.py --theme "seu tema"`
4. Aguarde a geração completa (~5-10 minutos)
5. Encontre seu vídeo na pasta `output/`

---

**Status Atual:** ⚠️ Aguardando configuração das chaves de API