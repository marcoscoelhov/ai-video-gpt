# 📱 AI Video GPT - Otimizado para TikTok

Sistema de geração automática de vídeos otimizado para o formato TikTok (9:16) usando IA.

## 🎯 Características do Formato TikTok

### ✅ Otimizações Implementadas

- **📐 Resolução**: 720x1280 (proporção 9:16)
- **🎨 Prompts Verticais**: Imagens otimizadas para composição vertical
- **📱 Mobile-First**: Otimizado para visualização em dispositivos móveis
- **📝 Legendas Automáticas**: Geração automática de legendas sincronizadas
- **🎵 Áudio Sincronizado**: Múltiplos arquivos de áudio concatenados automaticamente

### 🔧 Modificações Técnicas

1. **Prompts de Imagem**: Adicionados termos específicos para formato vertical:
   - "vertical composition"
   - "portrait orientation" 
   - "9:16 aspect ratio"
   - "optimized for mobile viewing"

2. **Resolução de Vídeo**: Configurada para 720x1280 no FFmpeg

3. **Pipeline Otimizado**: Suporte para múltiplos arquivos de áudio e legendas

## 🚀 Como Usar

### Método 1: Script Dedicado (Recomendado)

```bash
python generate_tiktok_video.py "Seu tema aqui"
```

**Exemplos:**
```bash
python generate_tiktok_video.py "Um gato ninja explorando Tóquio"
python generate_tiktok_video.py "Receita de bolo de chocolate em 30 segundos"
python generate_tiktok_video.py "Tutorial de dança futurista"
```

### Método 2: Script Principal

```bash
python src/main.py
```

## 📁 Estrutura de Saída

Após a geração, você encontrará na pasta `output/`:

```
output/
├── final_video.mp4          # 🎬 Vídeo final (720x1280)
├── image_001.png            # 🖼️ Imagens geradas
├── image_002.png
├── image_003.png
├── audio_scene_01.mp3       # 🎵 Arquivos de áudio
├── audio_scene_02.mp3
├── audio_scene_03.mp3
├── subtitles.srt            # 📝 Legendas
└── cost_report_*.json       # 💰 Relatório de custos
```

## 🔍 Verificação do Formato

Para confirmar que o vídeo está no formato correto:

```bash
# Verificar resolução
ffprobe -v quiet -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 output/final_video.mp4

# Deve retornar: 720x1280
```

## 📱 Teste de Qualidade

### ✅ Checklist de Verificação

- [ ] **Resolução**: 720x1280 (9:16)
- [ ] **Orientação**: Vertical/Retrato
- [ ] **Composição**: Elementos principais centralizados
- [ ] **Legibilidade**: Texto e elementos visíveis em tela pequena
- [ ] **Duração**: Adequada para TikTok (geralmente 15-60 segundos)
- [ ] **Legendas**: Sincronizadas e legíveis
- [ ] **Áudio**: Claro e bem sincronizado

### 🧪 Script de Teste

```bash
python test_tiktok_video.py
```

Este script:
1. Gera um vídeo de teste
2. Verifica a resolução automaticamente
3. Confirma que todas as etapas funcionaram

## 🎨 Dicas para Melhores Resultados

### 📝 Temas Recomendados

- **Tutoriais rápidos**: "Como fazer X em 30 segundos"
- **Histórias visuais**: "Aventura de um personagem em local Y"
- **Demonstrações**: "Processo de criação de Z"
- **Transformações**: "Antes e depois de X"

### 🎯 Palavras-chave Eficazes

- "rápido", "tutorial", "passo a passo"
- "incrível", "surpreendente", "viral"
- "dica", "truque", "segredo"
- "transformação", "evolução", "progresso"

## 🔧 Configurações Avançadas

### Personalizar Resolução

Para alterar a resolução, edite `src/assemble.py`:

```python
# Linha ~95
"-vf", "scale=720:1280:force_original_aspect_ratio=decrease,pad=720:1280:(ow-iw)/2:(oh-ih)/2,setsar=1,format=yuv420p",
```

### Ajustar Prompts

Para modificar os prompts de imagem, edite `src/prompt.py`:

```python
# Linha ~45
vertical_instructions = (
    "Vertical composition, portrait orientation, 9:16 aspect ratio, "
    "optimized for mobile viewing, centered subject, "
    "clear focal point, high contrast, vibrant colors."
)
```

## 📊 Custos Estimados

- **Imagens**: ~$0.01 por imagem (Gemini 2.0 Flash)
- **Áudio**: Gratuito (gTTS)
- **Legendas**: ~$0.0001 por minuto (Gemini 2.0 Flash)
- **Total por vídeo**: ~$0.03-0.05 USD

## 🐛 Solução de Problemas

### Erro: "GEMINI_API_KEY not set"
```bash
# Configure sua chave no arquivo .env
echo "GEMINI_API_KEY=sua_chave_aqui" > .env
```

### Erro: "ffmpeg not found"
```bash
# Windows (usando chocolatey)
choco install ffmpeg

# Ou baixe de: https://ffmpeg.org/download.html
```

### Vídeo não está em 9:16
- Verifique se as modificações em `assemble.py` estão corretas
- Confirme que o FFmpeg está usando os parâmetros corretos

## 🎉 Próximos Passos

1. **Teste o vídeo** em um dispositivo móvel
2. **Ajuste o tema** se necessário
3. **Faça upload** para TikTok, Instagram Reels, YouTube Shorts
4. **Monitore o engajamento** e ajuste futuros vídeos

---

**🚀 Pronto para criar conteúdo viral para TikTok!**

Para mais informações, consulte o README principal do projeto.