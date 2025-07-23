# Sistema de Presets de Imagem - AI Video GPT

Este documento explica como usar e modificar o sistema de presets de imagem do AI Video GPT.

## Arquivo de Configuração

O arquivo `image_presets_config.json` contém toda a configuração dos presets de imagem disponíveis no sistema.

### Estrutura do Arquivo

```json
{
  "image_presets": {
    "preset_key": {
      "name": "Nome de Exibição",
      "description": "Descrição do preset para o usuário",
      "prompt": "Prompt técnico que será aplicado às imagens"
    }
  },
  "default_preset": null,
  "description": "Descrição geral do sistema"
}
```

### Campos Explicados

- **preset_key**: Identificador único do preset (usado internamente)
- **name**: Nome que aparece na interface do usuário
- **description**: Descrição detalhada mostrada ao usuário
- **prompt**: Texto técnico que será adicionado aos prompts de imagem
- **default_preset**: Preset padrão (null = nenhum)

## Como Adicionar um Novo Preset

1. Abra o arquivo `src/config/image_presets_config.json`
2. Adicione uma nova entrada no objeto `image_presets`:

```json
"meu_novo_preset": {
  "name": "Meu Estilo",
  "description": "Descrição do meu novo estilo visual",
  "prompt": "Prompt técnico para gerar imagens neste estilo"
}
```

3. Salve o arquivo
4. Reinicie o servidor (o sistema carregará automaticamente o novo preset)

## Como Modificar um Preset Existente

1. Abra o arquivo `src/config/image_presets_config.json`
2. Encontre o preset que deseja modificar
3. Altere os campos `name`, `description` ou `prompt` conforme necessário
4. Salve o arquivo
5. Reinicie o servidor para aplicar as mudanças

## Como Remover um Preset

1. Abra o arquivo `src/config/image_presets_config.json`
2. Remova completamente a entrada do preset desejado
3. Salve o arquivo
4. Reinicie o servidor

## Validação no Backend

O sistema valida automaticamente os presets disponíveis. Se você adicionar um novo preset, também precisa atualizar a validação em `app.py`:

```python
# Encontre esta linha em app.py:
valid_presets = ['3d_cartoon', 'realistic', 'anime', 'digital_art']

# Adicione seu novo preset:
valid_presets = ['3d_cartoon', 'realistic', 'anime', 'digital_art', 'meu_novo_preset']
```

## Dicas para Criar Prompts Eficazes

1. **Seja específico**: Descreva claramente o estilo visual desejado
2. **Use termos técnicos**: Inclua termos como "lighting", "composition", "style"
3. **Mantenha consistência**: Use linguagem similar entre diferentes presets
4. **Teste iterativamente**: Gere algumas imagens e ajuste o prompt conforme necessário

## Exemplo de Prompt Bem Estruturado

```
"Create a [STYLE] image with [CHARACTERISTICS]. Use [LIGHTING] and [TECHNICAL_DETAILS]. Focus on [SPECIFIC_ELEMENTS]."
```

## Troubleshooting

### Preset não aparece na interface
- Verifique se o JSON está válido (use um validador JSON online)
- Certifique-se de que reiniciou o servidor
- Verifique o console do navegador para erros

### Preset não funciona corretamente
- Verifique se adicionou o preset na validação do backend
- Teste o prompt isoladamente para ver se produz os resultados esperados
- Verifique os logs do servidor para erros

### Erro ao carregar presets
- O sistema tem um fallback automático para presets padrão
- Verifique se o arquivo JSON não tem erros de sintaxe
- Verifique as permissões do arquivo

## Arquivos Relacionados

- `src/config/image_presets_config.json` - Configuração dos presets
- `src/parsers/image_prompts_parser.py` - Lógica de aplicação dos presets
- `app.py` - Validação e endpoint da API
- `src/frontend/script.js` - Interface do usuário
- `src/frontend/index.html` - Elementos HTML
- `src/frontend/styles.css` - Estilos visuais