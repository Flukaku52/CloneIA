# Fluxo de Trabalho Padrão para Criação de Reels

Este documento descreve o fluxo de trabalho padrão para criação de Reels usando o sistema FlukakuIA, com foco especial na sincronização perfeita entre áudio e vídeo.

## Visão Geral do Processo

O processo completo de criação de um Reel envolve as seguintes etapas:

1. **Geração do Script**: Criação do texto para o Reel, com marcadores de corte `[CORTE]`
2. **Geração de Áudio**: Conversão do texto em áudio usando a voz FlukakuIA no ElevenLabs
3. **Geração de Vídeo**: Criação dos vídeos para cada seção usando o HeyGen
4. **Concatenação**: União dos vídeos em um único Reel com sincronização perfeita

## Etapa 1: Geração do Script

O script deve seguir o formato padrão:

```
E aí cambada, Rapidinha na área e sem enrolação, vamo lá!

[CORTE]

Primeira notícia aqui...

[CORTE]

Segunda notícia aqui...

[CORTE]

Por hoje é só isso, galera! Vou trazer mais novidades em breve. Valeu!
```

Características importantes:
- Use `[CORTE]` para marcar onde haverá cortes no vídeo
- Evite usar "US$", substitua por "dólares"
- Mantenha cada seção concisa e direta
- Use linguagem informal e dinâmica

## Etapa 2: Geração de Áudio

Use o script `processar_script_com_cortes.py` para gerar os áudios:

```bash
./processar_script_com_cortes.py --arquivo scripts/seu_script.txt --gerar-audio
```

Este comando irá:
1. Dividir o script em seções usando os marcadores `[CORTE]`
2. Gerar um arquivo de áudio MP3 para cada seção
3. Salvar os arquivos em `output/audio/` com timestamps únicos

## Etapa 3: Geração de Vídeo

Use o script `gerar_video_com_cortes.py` para gerar os vídeos:

```bash
./gerar_video_com_cortes.py --timestamp YYYYMMDD_HHMMSS
```

Onde `YYYYMMDD_HHMMSS` é o timestamp dos arquivos de áudio gerados na etapa anterior.

Este comando irá:
1. Encontrar os arquivos de áudio com o timestamp especificado
2. Gerar um vídeo para cada arquivo de áudio usando o HeyGen
3. Salvar os vídeos em `output/videos/` com o mesmo timestamp

## Etapa 4: Concatenação (IMPORTANTE)

Use o script `concatenar_videos.py` para unir os vídeos em um único Reel:

```bash
./concatenar_videos.py --timestamp YYYYMMDD_HHMMSS
```

Este é o script padrão para concatenação e deve ser sempre usado para garantir a sincronização perfeita entre áudio e vídeo.

### Por que este script é especial?

O script `concatenar_videos.py` foi desenvolvido especificamente para resolver o problema de sincronização entre o áudio e o movimento labial nos vídeos do HeyGen. Ele:

1. **Preserva os timecodes originais** dos vídeos
2. **Não recodifica os clipes individualmente**, apenas os concatena
3. **Faz cortes secos** entre as notícias, sem transições
4. **Usa parâmetros avançados do FFmpeg** para garantir sincronização perfeita:
   - `-f concat -safe 0`: Modo de concatenação que preserva metadados
   - `-fflags +genpts -fps_mode cfr`: Garante frame rate constante
   - `-copyts -avoid_negative_ts make_zero`: Preserva timestamps
   - `-async 1`: Alinha o áudio para manter a sincronização

O resultado é um vídeo único com cortes entre as notícias, mantendo o áudio e o movimento labial 100% sincronizados, sem variações de pitch ou frame drops.

## Gerenciamento de Contas HeyGen

Para alternar entre diferentes contas do HeyGen:

```bash
./gerenciar_contas.py ativar --id conta3
```

Ou ao gerar vídeos:

```bash
./gerar_video_com_cortes.py --timestamp YYYYMMDD_HHMMSS --conta conta3
```

## Dicas para Resultados Ótimos

1. **Verifique os áudios** antes de gerar os vídeos
2. **Use o script `concatenar_videos.py`** para unir os vídeos, não outros métodos
3. **Mantenha os scripts concisos** para melhor engajamento
4. **Verifique o vídeo final** antes de publicar

## Exemplo de Fluxo Completo

```bash
# 1. Gerar áudios
./processar_script_com_cortes.py --arquivo scripts/rapidinha_bitcoin.txt --gerar-audio

# 2. Gerar vídeos (usando o timestamp dos áudios gerados)
./gerar_video_com_cortes.py --timestamp 20250515_1200

# 3. Concatenar vídeos (usando o mesmo timestamp)
./concatenar_videos.py --timestamp 20250515_1200
```

O vídeo final estará disponível em `output/videos/final/` com o timestamp atual.
