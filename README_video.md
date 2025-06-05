# Geração de Vídeo para "Rapidinha no Cripto"

Este guia explica como usar o sistema para gerar vídeos completos para o quadro "Rapidinha no Cripto".

## Pré-requisitos

1. Python 3.8+
2. Dependências instaladas (`pip install -r requirements.txt`)
3. Chaves de API configuradas no arquivo `.env`:
   - `OPENAI_API_KEY`: Para gerar explicações personalizadas
   - `ELEVENLABS_API_KEY`: Para gerar áudio com voz clonada (opcional)

## Configuração da Voz

Para obter melhores resultados, você pode clonar sua voz usando a API da ElevenLabs:

1. Obtenha uma chave de API da ElevenLabs em [https://elevenlabs.io](https://elevenlabs.io)
2. Adicione a chave ao arquivo `.env`:
   ```
   ELEVENLABS_API_KEY=sua_chave_elevenlabs_aqui
   ```
3. Clone sua voz a partir dos vídeos de referência:
   ```
   python rapidinha_video_creator.py clone-voice
   ```

## Geração de Vídeo

### Opção 1: Vídeo Completo

Para gerar um vídeo completo com notícias reais e explicações de IA:

```
python rapidinha_video_creator.py create
```

### Opção 2: Vídeo com Notícias Simuladas

Para gerar um vídeo com notícias simuladas:

```
python rapidinha_video_creator.py create --mock
```

### Opção 3: Vídeo Simples

Para gerar um vídeo simples (apenas texto sobre fundo colorido):

```
python rapidinha_video_creator.py create --simple
```

## Listar Vídeos Gerados

Para listar todos os vídeos gerados anteriormente:

```
python rapidinha_video_creator.py list
```

## Estrutura de Arquivos

- `output/audio/`: Arquivos de áudio gerados
- `output/videos/`: Vídeos finais gerados
- `reference/videos/`: Vídeos de referência para análise de estilo e clonagem de voz
- `reference/voice_samples/`: Amostras de áudio extraídas para clonagem de voz

## Fluxo de Trabalho

1. **Geração de Script**: O sistema coleta notícias e gera um script no seu estilo de comunicação
2. **Geração de Áudio**: O script é convertido em áudio usando a API da ElevenLabs
3. **Geração de Vídeo**: O áudio é combinado com elementos visuais para criar o vídeo final

## Solução de Problemas

- **Erro na geração de áudio**: Verifique se a chave da API da ElevenLabs está correta
- **Erro na geração de vídeo**: Verifique se todas as dependências estão instaladas
- **Vídeos sem áudio**: Verifique se o FFmpeg está instalado no sistema

## Próximos Passos

- Melhorar a qualidade visual dos vídeos
- Adicionar mais opções de personalização
- Implementar upload automático para redes sociais
