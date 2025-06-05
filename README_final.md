# Clone IA para "Rapidinha no Cripto"

Este projeto cria um clone de IA que imita seu estilo de comunicação e sua voz para gerar automaticamente conteúdo para o quadro "Rapidinha no Cripto".

## Funcionalidades Implementadas

1. **Análise do seu estilo de comunicação**:
   - Extrai e analisa seu estilo a partir dos vídeos de referência
   - Cria um prompt personalizado para a IA gerar conteúdo no seu estilo

2. **Geração de scripts personalizados**:
   - Gera scripts no seu estilo para o quadro "Rapidinha no Cripto"
   - Integra com a API da OpenAI para explicações personalizadas

3. **Clonagem de voz**:
   - Extrai amostras de áudio dos seus vídeos
   - Usa a API da ElevenLabs para clonar sua voz
   - Gera áudio com sua voz clonada para os scripts

4. **Geração de vídeos**:
   - Gera vídeos simples com o script e o áudio
   - Integração com HeyGen para vídeos com seu clone visual

## Como Usar

### Configuração

1. Clone o repositório
2. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```
3. Configure as chaves de API no arquivo `.env`:
   ```
   OPENAI_API_KEY=sua_chave_openai_aqui
   ELEVENLABS_API_KEY=sua_chave_elevenlabs_aqui
   HEYGEN_API_KEY=sua_chave_heygen_aqui
   ```

### Geração de Scripts

```
python rapidinha_generator_ai.py
```

### Extração de Amostras de Áudio

```
python audio_generator.py --extract
```

### Clonagem de Voz

```
python audio_generator.py --clone
```

### Geração de Áudio

```
python audio_generator.py --text "Texto para gerar áudio"
```

### Geração de Vídeo Simples

```
python rapidinha_video_creator.py create --simple
```

### Geração de Vídeo com HeyGen

Para gerar vídeos com seu clone visual usando o HeyGen, siga estas etapas:

1. Acesse [app.heygen.com](https://app.heygen.com)
2. Faça login na sua conta
3. Vá para "Avatars" > "Photo Avatars"
4. Crie um novo avatar usando suas fotos ou vídeos
5. Vá para "Create" > "AI Studio"
6. Selecione seu avatar personalizado
7. Faça upload do áudio gerado pelo nosso sistema
8. Gere o vídeo

Você também pode usar a API do HeyGen para automatizar esse processo, mas isso requer um plano pago.

## Arquivos Importantes

- `rapidinha_generator_ai.py`: Gerador de scripts no seu estilo
- `audio_generator.py`: Extrator de amostras de áudio e gerador de áudio com voz clonada
- `rapidinha_video_creator.py`: Gerador de vídeos simples
- `config/voice_config.json`: Configuração da sua voz clonada
- `reference/videos/`: Vídeos de referência
- `reference/voice_samples/`: Amostras de áudio extraídas
- `scripts/`: Scripts gerados
- `output/audio/`: Áudios gerados
- `output/videos/`: Vídeos gerados

## Limitações Atuais

1. **Geração de vídeos com clone visual**: A API do HeyGen para geração de vídeos com avatares personalizados requer um plano pago.
2. **Qualidade da clonagem de voz**: A qualidade da voz clonada depende da quantidade e qualidade das amostras de áudio.
3. **Integração com redes sociais**: Ainda não há integração automática para publicação nas redes sociais.

## Próximos Passos

1. **Melhorar a qualidade visual dos vídeos**:
   - Implementar uma versão mais avançada do gerador de vídeos
   - Adicionar elementos visuais como gráficos e animações

2. **Automatizar o processo**:
   - Criar um script que execute todo o processo automaticamente
   - Implementar um agendador para gerar vídeos periodicamente

3. **Integrar com redes sociais**:
   - Adicionar funcionalidade para publicar os vídeos automaticamente
   - Implementar análise de métricas de engajamento
