# Integração Google Gemini 2.0 Flash - Geração de Imagens

Este documento descreve como usar a nova integração com o Google Gemini 2.0 Flash para geração de imagens no projeto AI Video GPT.

## 🚀 Visão Geral

A integração com o Google Gemini 2.0 Flash oferece capacidades nativas de geração de imagens através de uma API simplificada, substituindo a necessidade do Vertex AI. O Gemini 2.0 Flash Experimental inclui suporte nativo para geração de imagens multimodais.

### Vantagens do Gemini 2.0 Flash

- ✅ **Configuração Simplificada**: Apenas uma API key necessária
- ✅ **Suporte Nativo**: Geração de imagens integrada ao modelo
- ✅ **API Direta**: Sem necessidade de configuração complexa do Vertex AI
- ✅ **Multimodal**: Suporte para texto e imagem na mesma requisição
- ✅ **Edição de Imagens**: Capacidade de editar imagens existentes

## 📦 Instalação

### 1. Instalar Dependências

```bash
pip install -r requirements.txt
```

As principais dependências incluem:
- `google-genai>=0.3.0` - API do Google Gemini
- `Pillow>=10.0.0` - Processamento de imagens

### 2. Configurar API Key

Obtenha sua API key do Google AI Studio:
1. Acesse: https://aistudio.google.com/app/apikey
2. Crie uma nova API key
3. Configure a variável de ambiente:

**Windows:**
```cmd
set GEMINI_API_KEY=sua_api_key_aqui
```

**Linux/Mac:**
```bash
export GEMINI_API_KEY=sua_api_key_aqui
```

**Ou crie um arquivo `.env`:**
```
GEMINI_API_KEY=sua_api_key_aqui
```

## 🎯 Uso Básico

### Exemplo Simples

```python
from gemini_imagen_client import GeminiImagenClient

# Inicializar cliente
client = GeminiImagenClient()

# Gerar imagem
result = client.generate_image(
    prompt="Um gato astronauta dirigindo um buggy lunar",
    output_path="minha_imagem.png"
)

print(f"Imagem salva em: {result['saved_path']}")
```

### Função de Conveniência

```python
from gemini_imagen_client import generate_image_quick

# Geração rápida
path = generate_image_quick(
    prompt="Uma cidade futurista ao pôr do sol",
    output_path="cidade_futurista.png"
)
```

## 🔧 Funcionalidades Avançadas

### 1. Geração Múltipla

```python
prompts = [
    "Um dragão voando sobre montanhas",
    "Uma floresta mágica bioluminescente",
    "Um robô jardineiro cuidando de flores"
]

results = client.generate_multiple_images(
    prompts=prompts,
    output_dir="imagens/",
    filename_prefix="fantasia"
)
```

### 2. Geração Assíncrona

```python
import asyncio

async def gerar_async():
    results = await client.generate_multiple_images_async(
        prompts=prompts,
        output_dir="async_images/",
        max_concurrent=3
    )
    return results

# Executar
results = asyncio.run(gerar_async())
```

### 3. Edição de Imagens

```python
# Editar uma imagem existente
result = client.edit_image(
    image_path="imagem_original.png",
    edit_prompt="Adicione um chapéu vermelho no personagem",
    output_path="imagem_editada.png"
)
```

## 📁 Estrutura do Projeto

```
ai-video-gpt/
├── gemini_imagen_client.py      # Cliente principal
├── examples/
│   └── gemini_imagen_example.py # Exemplos de uso
├── requirements.txt             # Dependências atualizadas
├── GEMINI_IMAGEN_README.md     # Esta documentação
└── tasks/
    └── todo.md                 # Plano de implementação
```

## 🧪 Executar Exemplos

```bash
# Executar todos os exemplos
python examples/gemini_imagen_example.py

# Ou executar exemplos específicos
python -c "from examples.gemini_imagen_example import exemplo_basico; exemplo_basico()"
```

## 📋 API Reference

### Classe GeminiImagenClient

#### Métodos Principais

- `generate_image(prompt, output_path=None, include_text_response=True)`
- `generate_image_async(prompt, output_path=None, include_text_response=True)`
- `generate_multiple_images(prompts, output_dir=None, filename_prefix="gemini_image")`
- `generate_multiple_images_async(prompts, output_dir=None, max_concurrent=3)`
- `edit_image(image_path, edit_prompt, output_path=None)`
- `get_model_info()`

#### Parâmetros de Inicialização

- `api_key` (opcional): Chave da API do Gemini
- `model_name` (padrão: "gemini-2.0-flash-exp"): Nome do modelo

#### Formato de Retorno

Todos os métodos de geração retornam um dicionário:

```python
{
    'image': PIL.Image,           # Objeto da imagem gerada
    'text_response': str,         # Resposta de texto (opcional)
    'saved_path': str,           # Caminho onde foi salva (se fornecido)
    'prompt': str,               # Prompt usado (em métodos múltiplos)
    'index': int,                # Índice (em métodos múltiplos)
    'error': str                 # Erro (se houver)
}
```

## 🔍 Troubleshooting

### Problemas Comuns

1. **Erro de API Key**
   ```
   ValueError: API key não fornecida
   ```
   - Verifique se a variável `GEMINI_API_KEY` está definida
   - Confirme se a API key é válida

2. **Erro de Dependências**
   ```
   ImportError: PIL (Pillow) é necessário
   ```
   - Execute: `pip install Pillow`

3. **Erro de Modelo**
   ```
   Modelo não encontrado
   ```
   - Verifique se está usando `gemini-2.0-flash-exp`
   - Confirme se sua conta tem acesso ao modelo experimental

### Logs e Debug

Para debug detalhado, você pode capturar exceções:

```python
try:
    result = client.generate_image(prompt="teste")
except Exception as e:
    print(f"Erro detalhado: {e}")
    # Adicionar logging conforme necessário
```

## 🔄 Migração do Vertex AI

Se você estava usando Vertex AI anteriormente:

1. **Remover dependências antigas:**
   ```bash
   pip uninstall google-cloud-aiplatform vertexai
   ```

2. **Instalar nova dependência:**
   ```bash
   pip install google-genai
   ```

3. **Atualizar código:**
   ```python
   # Antes (Vertex AI)
   # from google.cloud import aiplatform
   
   # Depois (Gemini 2.0 Flash)
   from gemini_imagen_client import GeminiImagenClient
   ```

## 📚 Recursos Adicionais

- [Documentação Oficial do Gemini API](https://ai.google.dev/gemini-api/docs)
- [Google AI Studio](https://aistudio.google.com/)
- [Exemplos da Comunidade](https://github.com/google-gemini/cookbook)

## 🤝 Contribuição

Para contribuir com melhorias:

1. Fork o projeto
2. Crie uma branch para sua feature
3. Implemente suas mudanças
4. Adicione testes se necessário
5. Submeta um Pull Request

## 📄 Licença

Este projeto segue a mesma licença do projeto principal AI Video GPT.

---

**Nota**: Esta integração utiliza o modelo experimental `gemini-2.0-flash-exp`. Funcionalidades e disponibilidade podem mudar conforme o modelo evolui.