# Migração para ElevenLabs TTS

## Visão Geral

Este documento descreve a migração da funcionalidade de narração do sistema de gTTS para ElevenLabs, oferecendo narração de alta qualidade com suporte a múltiplos idiomas e tipos de voz.

## Benefícios da Migração

### ✅ Qualidade Superior
- **Vozes mais naturais**: ElevenLabs oferece vozes sintéticas de alta qualidade
- **Melhor prosódia**: Entonação e ritmo mais naturais
- **Suporte multilíngue**: Melhor suporte para português brasileiro

### ✅ Flexibilidade
- **Múltiplos tipos de voz**: narrator, male, female, child
- **Vozes personalizadas**: Suporte a voice cloning (futuro)
- **Controle de velocidade e tom**: Configurações avançadas

### ✅ Compatibilidade
- **Fallback automático**: Usa gTTS se ElevenLabs não estiver disponível
- **Detecção de idioma**: Detecta automaticamente o idioma do texto
- **API consistente**: Mesma interface para ambos os provedores

## Arquitetura

### Estrutura de Arquivos

```
config/
├── voice_config.py          # Configurações centralizadas de voz
├── elevenlabs_client.py     # Cliente para API do ElevenLabs
core/
├── voice.py                 # Módulo principal de TTS (atualizado)
```

### Fluxo de Funcionamento

1. **Seleção de Provedor**
   - `auto`: Prefere ElevenLabs se disponível, senão gTTS
   - `elevenlabs`: Força uso do ElevenLabs
   - `gtts`: Força uso do gTTS

2. **Detecção de Idioma**
   - Automática baseada no texto
   - Configuração manual via parâmetro `language`

3. **Geração de Áudio**
   - ElevenLabs: API REST com modelo multilíngue
   - gTTS: Fallback para compatibilidade

## Configuração

### 1. Chave de API

Adicione sua chave do ElevenLabs no arquivo `.env`:

```bash
# Obrigatório
GEMINI_API_KEY=sua_chave_gemini

# Opcional (para ElevenLabs)
ELEVENLABS_API_KEY=sua_chave_elevenlabs
```

### 2. Instalação de Dependências

```bash
pip install elevenlabs>=0.2.26
```

### 3. Configurações Padrão

As configurações estão em `config/voice_config.py`:

```python
# Vozes recomendadas para português
RECOMMENDED_VOICES_PT = {
    'narrator': 'pNInz6obpgDQGcFmaJgB',  # Adam (multilingual)
    'male': 'VR6AewLTigWG4xSOukaG',     # Arnold (multilingual) 
    'female': 'EXAVITQu4vr4xnSDxMaL',   # Bella (multilingual)
    'child': 'yoZ06aMxZJJ28mfd3POQ'     # Sam (multilingual)
}
```

## Uso

### 1. Via Linha de Comando

```bash
# Usar ElevenLabs automaticamente (se disponível)
python main.py --theme "robô futurista" --voice-provider auto

# Forçar ElevenLabs com voz feminina
python main.py --theme "robô futurista" --voice-provider elevenlabs --voice-type female

# Especificar idioma
python main.py --theme "robô futurista" --language pt-br

# Usar apenas gTTS
python main.py --theme "robô futurista" --voice-provider gtts
```

### 2. Via Código Python

```python
from core.voice import tts_scenes

# Usar ElevenLabs com configurações padrão
audio_paths = tts_scenes(
    script_data, 
    output_dir,
    provider='elevenlabs',
    voice_type='female',
    language='pt-br'
)

# Usar provedor automático
audio_paths = tts_scenes(
    script_data, 
    output_dir,
    provider='auto'  # Prefere ElevenLabs se disponível
)
```

### 3. Funções de Conveniência

```python
from core.voice import tts_scenes_elevenlabs, tts_scenes_gtts

# Usar apenas ElevenLabs
audio_paths = tts_scenes_elevenlabs(script_data, output_dir)

# Usar apenas gTTS
audio_paths = tts_scenes_gtts(script_data, output_dir)
```

## Tipos de Voz Disponíveis

| Tipo | Descrição | Uso Recomendado |
|------|-----------|----------------|
| `narrator` | Voz neutra para narração | Documentários, explicações |
| `male` | Voz masculina | Personagens masculinos |
| `female` | Voz feminina | Personagens femininos |
| `child` | Voz jovem | Conteúdo infantil |

## Idiomas Suportados

- **Português Brasileiro**: `pt-br` (padrão para texto em português)
- **Inglês**: `en-us` (padrão para texto em inglês)
- **Detecção automática**: O sistema detecta o idioma baseado no texto

## Tratamento de Erros

### Fallback Automático

O sistema implementa fallback automático:

1. **ElevenLabs falha** → Usa gTTS
2. **API key não configurada** → Usa gTTS
3. **Limite de API atingido** → Usa gTTS

### Logs de Debug

```python
# Ativar logs detalhados
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Custos e Limites

### ElevenLabs
- **Plano gratuito**: 10.000 caracteres/mês
- **Plano pago**: A partir de $5/mês
- **Custo por caractere**: Varia conforme o plano

### gTTS (Fallback)
- **Gratuito**: Sem limites conhecidos
- **Limitações**: Qualidade inferior, menos natural

## Testes

### Teste Manual

```bash
# Testar o módulo de voz diretamente
python core/voice.py
```

### Teste com Projeto Real

```bash
# Gerar vídeo com ElevenLabs
python main.py --theme "teste de voz" --voice-provider elevenlabs
```

## Solução de Problemas

### Erro: "ElevenLabs API key not found"

**Solução**: Configure `ELEVENLABS_API_KEY` no arquivo `.env`

### Erro: "Voice ID not found"

**Solução**: Verifique se o voice_id existe na sua conta ElevenLabs

### Qualidade de áudio ruim

**Solução**: 
1. Verifique se está usando ElevenLabs (não gTTS)
2. Teste diferentes tipos de voz
3. Ajuste configurações de qualidade

### Fallback para gTTS inesperado

**Solução**:
1. Verifique logs de erro
2. Confirme API key válida
3. Verifique limite de caracteres

## Roadmap Futuro

### Funcionalidades Planejadas

- [ ] **Voice Cloning**: Suporte a vozes personalizadas
- [ ] **Configurações avançadas**: Velocidade, tom, ênfase
- [ ] **Cache de áudio**: Evitar regeneração desnecessária
- [ ] **Múltiplos provedores**: Azure, AWS Polly
- [ ] **Interface web**: Configuração via interface gráfica

### Melhorias de Performance

- [ ] **Processamento paralelo**: Gerar múltiplos áudios simultaneamente
- [ ] **Compressão otimizada**: Reduzir tamanho dos arquivos
- [ ] **Streaming**: Reprodução durante geração

## Contribuição

Para contribuir com melhorias:

1. Teste diferentes configurações de voz
2. Reporte bugs ou limitações
3. Sugira novas funcionalidades
4. Contribua com documentação

## Referências

- [ElevenLabs API Documentation](https://docs.elevenlabs.io/)
- [ElevenLabs Python SDK](https://github.com/elevenlabs/elevenlabs-python)
- [gTTS Documentation](https://gtts.readthedocs.io/)