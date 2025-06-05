# Guia para Extrair Amostras de Áudio dos Reels com Audacity

Este guia vai ajudar você a extrair amostras de áudio de 31-36 segundos dos seus reels usando o Audacity.

## Passo 1: Extrair Áudio dos Vídeos

Primeiro, vamos extrair o áudio dos seus vídeos para facilitar o trabalho no Audacity:

1. Abra o Terminal
2. Execute o script de extração de áudio:

```bash
cd /Users/renatosantannasilva/Documents/augment-projects/CloneIA
python extract_audio_for_audacity.py
```

Este script:
- Extrairá o áudio de todos os vídeos na pasta `reference/videos`
- Salvará os arquivos de áudio na pasta `reference/audio_for_audacity`
- Criará instruções detalhadas para o processo no Audacity

> **Nota**: O script tentará instalar o FFmpeg se não estiver disponível. Se a instalação automática falhar, siga as instruções fornecidas para instalar manualmente.

## Passo 2: Abrir o Audacity

1. Abra o Audacity no seu computador
2. Se for a primeira vez que está usando, configure as preferências:
   - Vá em **Audacity > Preferências** (ou **Editar > Preferências** no Windows)
   - Em **Qualidade**, defina:
     - Taxa de amostragem padrão: 44100 Hz
     - Formato de amostra padrão: 16 bits
     - Canais padrão: Mono

## Passo 3: Importar Áudio no Audacity

1. No Audacity, vá em **Arquivo > Importar > Áudio**
2. Navegue até a pasta `/Users/renatosantannasilva/Documents/augment-projects/CloneIA/reference/audio_for_audacity`
3. Selecione um dos arquivos de áudio extraídos e clique em **Abrir**

## Passo 4: Identificar e Selecionar Segmentos de Qualidade

Para cada arquivo de áudio:

1. **Ouça o áudio completo** para identificar segmentos com:
   - Fala clara e natural
   - Sem ruído de fundo ou interferências
   - Sem hesitações ou pausas longas
   - Expressões características como "E aí cambada!"
   - Frases completas e coerentes

2. **Selecione um segmento de 31-36 segundos**:
   - Clique e arraste para selecionar uma parte do áudio
   - Verifique a duração na barra de status na parte inferior da janela
   - Ajuste a seleção até obter entre 31 e 36 segundos
   - Ouça a seleção pressionando a tecla de espaço para confirmar a qualidade

3. **Dicas para seleção ideal**:
   - Comece a seleção no início de uma frase
   - Termine a seleção no final de uma frase
   - Evite cortar palavras no meio
   - Inclua variações de entonação e expressividade
   - Priorize trechos onde você fala de forma fluida e natural

## Passo 5: Exportar a Seleção

Para cada segmento selecionado:

1. Com o segmento selecionado, vá em **Arquivo > Exportar > Exportar seleção como WAV**
2. Navegue até a pasta `/Users/renatosantannasilva/Documents/augment-projects/CloneIA/reference/samples`
3. Dê um nome descritivo ao arquivo, como:
   - `intro_eai_cambada_1.wav`
   - `explicacao_bitcoin_1.wav`
   - `frase_rapida_1.wav`
   - `conclusao_1.wav`
4. Mantenha o formato como **WAV (Microsoft) 16 bit PCM**
5. Clique em **Salvar**

## Passo 6: Repetir o Processo

1. Continue selecionando e exportando diferentes segmentos do mesmo áudio
2. Quando terminar com um arquivo, feche-o e abra o próximo
3. Repita os passos 3-5 para cada arquivo de áudio

## Passo 7: Organizar as Amostras

Após extrair todas as amostras:

1. Verifique se todos os arquivos estão na pasta `reference/samples`
2. Confirme que cada arquivo tem entre 31 e 36 segundos
3. Verifique a qualidade de cada amostra reproduzindo-a

## Dicas para Obter as Melhores Amostras

- **Priorize qualidade sobre quantidade**: 10-15 amostras excelentes são melhores que 30 medianas
- **Diversifique o conteúdo**: Inclua diferentes tipos de frases e entonações
- **Inclua sua introdução característica**: "E aí cambada!" é uma marca registrada sua
- **Capture seu ritmo natural**: Selecione trechos onde você fala no seu ritmo normal, sem pausas artificiais
- **Verifique a qualidade do áudio**: Evite trechos com ruídos, ecos ou distorções

## Próximos Passos

Depois de extrair as amostras:

1. Use-as para treinar seu clone de voz no ElevenLabs
2. Compare os resultados com versões anteriores
3. Ajuste as configurações conforme necessário

Seguindo este guia, você obterá amostras de alta qualidade que ajudarão a melhorar significativamente a naturalidade e fluidez do seu clone de voz.
