# Vertex AI Imagen - Interface Simplificada

Esta biblioteca fornece uma interface simplificada e amigável para usar o Google Vertex AI Imagen para geração de imagens.

## Instalação

Certifique-se de que as dependências estão instaladas:

```bash
pip install google-cloud-aiplatform vertexai
```

## Configuração

### 1. Configurar Google Cloud

1. Crie um projeto no [Google Cloud Console](https://console.cloud.google.com/)
2. Ative a API Vertex AI
3. Configure a autenticação:

```bash
# Opção 1: Application Default Credentials (recomendado)
gcloud auth application-default login

# Opção 2: Service Account (para produção)
# Baixe o arquivo JSON da service account e defina:
export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account-key.json"
```

### 2. Configurar Variáveis de Ambiente

Adicione ao seu arquivo `.env`:

```env
GOOGLE_CLOUD_PROJECT=seu-projeto-id
GOOGLE_CLOUD_LOCATION=us-central1
```

## Uso

### Exemplo Básico (Assíncrono)

```python
import asyncio
from vertex_ai_imagen import ImagenClient

async def main():
    client = ImagenClient(project_id="gen-lang-client-0003871542")
    client.setup_credentials_from_env()  # ou .setup_credentials("key.json")
    
    image = await client.generate(
        prompt="Uma paisagem futurista com céu roxo",
        model="imagen-4.0-fast-generate-preview-06-06",
        aspect_ratio="16:9",
        count=1
    )
    image.save("saida.png")

asyncio.run(main())
```

### Exemplo Síncrono

```python
from vertex_ai_imagen import ImagenClient

client = ImagenClient(project_id="seu-projeto-id")
client.setup_credentials_from_env()

image = client.generate_sync(
    prompt="Um robô amigável em um jardim colorido",
    model="imagen-3.0-generate-002",
    aspect_ratio="1:1",
    count=1
)
image.save("robot.png")
```

### Função de Conveniência

```python
from vertex_ai_imagen import generate_image

# Geração rápida de uma imagem
image = generate_image(
    prompt="Uma cidade cyberpunk à noite",
    project_id="seu-projeto-id",
    aspect_ratio="16:9",
    output_file="cidade.png"
)
```

## API Reference

### ImagenClient

#### `__init__(project_id, location="us-central1")`

Cria uma nova instância do cliente.

- `project_id`: ID do projeto Google Cloud
- `location`: Região do Google Cloud (padrão: us-central1)

#### `setup_credentials_from_env()`

Configura credenciais usando Application Default Credentials.

#### `setup_credentials(key_file)`

Configura credenciais usando um arquivo de chave de service account.

- `key_file`: Caminho para o arquivo JSON da service account

#### `async generate(prompt, model, aspect_ratio, count)`

Gera uma imagem de forma assíncrona.

- `prompt`: Descrição textual da imagem
- `model`: Nome do modelo (padrão: "imagen-3.0-generate-002")
- `aspect_ratio`: Proporção da imagem ("1:1", "16:9", "9:16", "4:3")
- `count`: Número de imagens (atualmente apenas 1 é suportado)

#### `generate_sync(prompt, model, aspect_ratio, count)`

Versão síncrona do método `generate()`.

### ImageResponse

#### `save(filename)`

Salva a imagem gerada em um arquivo.

- `filename`: Caminho onde salvar a imagem

## Modelos Suportados

- `imagen-3.0-generate-002` (padrão)
- `imagen-4.0-fast-generate-preview-06-06` (mapeado para imagen-3.0)
- `imagen-4.0` (mapeado para imagen-3.0)
- `imagen-3.0` (mapeado para imagen-3.0)

## Aspect Ratios Suportados

- `1:1` - Quadrado
- `16:9` - Widescreen
- `9:16` - Vertical/Mobile
- `4:3` - Tradicional

## Exemplos de Teste

Execute os scripts de exemplo:

```bash
# Teste completo
python test_vertex_ai_imagen.py

# Exemplo do usuário
python example_usage.py
```

## Troubleshooting

### Erro de Autenticação

Se você receber erros de autenticação:

1. Verifique se executou `gcloud auth application-default login`
2. Confirme que o projeto está correto no `.env`
3. Verifique se a API Vertex AI está ativada

### Modelo Não Encontrado

Se o modelo não for encontrado:

1. Use `imagen-3.0-generate-002` (modelo padrão)
2. Verifique se sua região suporta o modelo

### Dependências

Se houver erros de importação:

```bash
pip install --upgrade google-cloud-aiplatform vertexai
```

## Estrutura do Projeto

```
├── vertex_ai_imagen.py      # Biblioteca principal
├── test_vertex_ai_imagen.py # Testes completos
├── example_usage.py         # Exemplo do usuário
└── README_vertex_ai_imagen.md # Esta documentação
```

## Contribuição

Esta é uma interface simplificada criada para facilitar o uso do Google Vertex AI Imagen. Para funcionalidades avançadas, consulte a documentação oficial do Vertex AI.