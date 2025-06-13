# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CloneIA is an AI-powered content generation system for creating "Rapidinha no Cripto" (Quick Crypto Updates) videos. It generates complete crypto news content by:
- Cloning the presenter's voice using ElevenLabs API
- Creating AI avatar videos using HeyGen API
- Generating scripts that mimic the presenter's communication style
- Processing crypto news from various APIs
- Using ML to learn and replicate the presenter's unique speaking patterns

## Key Commands

### Video Generation Commands
```bash
# MÉTODO PADRÃO PARA REELS PERSONALIZADOS
python gerar_reel_renato_melhorado.py

# Limpar outputs mantendo só arquivos finais
python limpar_outputs_manter_final.py

# Mostrar instruções para HeyGen
python instruções_heygen_final.py

# MÉTODOS ALTERNATIVOS (notícias automáticas)
python lança_a_boa.py
python generate_reel_correto.py
python ia_system/automation/pipeline.py
```

### Testing Commands
```bash
# Test HeyGen video generation
python test_optimized_generator.py --generate

# List available HeyGen avatars
python test_optimized_generator.py --list-avatars

# Test avatar rotation system
python testar_rotacao.py

# Test first segment of video
python test_primeiro_segmento.py
```

### Audio Commands
```bash
# Extract audio samples from reference videos
python audio_generator.py --extract

# Clone voice using extracted samples
python audio_generator.py --clone

# Generate audio from text
python audio_generator.py --text "Text to convert to speech"
```

### Utility Commands
```bash
# Add new avatar to system
python adicionar_avatar.py

# Configure notifications
python configurar_notificacoes.py

# View latest news
python ultimas_noticias.py

# View system alerts
python ver_alertas.py
```

## Architecture Overview

### Core Modules (`core/`)
- **audio.py**: ElevenLabs API integration (voice ID: oG30eP3GaYrCwnabbDCw)
- **video.py**: MoviePy video creation with intro animations and transitions
- **text.py**: Text optimization for natural speech synthesis
- **utils.py**: API key management and file operations

### IA System (`ia_system/`)
- **automation/**: Complete pipeline and monitoring systems
- **news_collector.py**: Aggregates crypto news from multiple sources
- **script_generator.py**: Generates scripts mimicking presenter's style
- **twitter_collector.py**: Real-time Twitter monitoring
- **notificador.py**: Priority-based notification system
- **cache/**: Caches news and API responses

### ML Training (`ml_training/`)
- **gerador_roteiro_ia.py**: AI-powered script generation
- **analisador_roteiros.py**: Analyzes scripts to learn patterns
- **roteiros_exemplos/**: Example scripts for pattern learning

### Configuration System
Configuration files in `config/`:
- **configuracoes_padrao_sistema.json**: System defaults and API endpoints
- **avatares_sistema.json**: HeyGen avatar configurations (5 avatars with rotation)
- **voice_config_*.json**: Voice profiles (fluido, carioca_fluido, ultra_natural)
- **heygen_profiles.json**: Multiple HeyGen accounts with quotas
- **ia_settings.json**: News criteria and script structure
- **video_dimensions.json**: Video format (portrait 9:16, 1080x1920)

### API Integration Flow
1. **News Collection**: CryptoCompare, NewsAPI, Twitter → Cross-verification
2. **Script Generation**: OpenAI API with presenter's style patterns
3. **Audio Creation**: ElevenLabs API with optimized voice settings
4. **Video Generation**: HeyGen API for AI avatar or MoviePy for simple videos

### Working with Voice Profiles
Multiple voice configurations for different effects:
- **fluido**: Natural flowing speech (stability: 0.2, similarity_boost: 0.7)
- **carioca_fluido**: Regional accent variation
- **ultra_natural**: Maximum naturalness settings

### HeyGen Avatar Management
- **CONFIGURAÇÃO PADRÃO PARA REELS**: Avatar `bd9548bed4984738a93b0db0c6c3edc9`
- **Voice ID padrão**: `25NR0sM9ehsgXaoknsxO` (FlukakuFluido)
- **Formato obrigatório**: 9:16 Portrait
- **Método recomendado**: Interface web do HeyGen (API instável)
- **Background**: Escuro (#000000)
- **Estrutura**: 5 segmentos com cortes secos

## Important Notes

- **API Keys**: Required in `.env`: OPENAI_API_KEY, ELEVENLABS_API_KEY, HEYGEN_API_KEY, CRYPTOCOMPARE_API_KEY, NEWSAPI_KEY
- **Voice Samples**: Store in `reference/voice_samples/` (7-12 seconds each, 20-40 samples)
- **Output Structure**: `output/audio/` and `output/videos/` with timestamped files
- **Presenter Style**: Uses specific phrases like "EAÍCAMBADA", "cambada", libertarian tone
- **Target Duration**: 2-3 minutes for optimal engagement
- **News Priority**: High/Medium/Low based on market impact and relevance

## CONFIGURAÇÃO PADRÃO PARA REELS

**⚠️ IMPORTANTE: SEMPRE use estas configurações para gerar reels:**

### Configurações Obrigatórias
- **Voice ID**: `25NR0sM9ehsgXaoknsxO` (FlukakuFluido)
- **Avatar ID**: `bd9548bed4984738a93b0db0c6c3edc9`
- **Formato**: 9:16 Portrait (1080x1920)
- **Background**: Escuro (#000000)
- **API Key HeyGen**: `OGU5OTA4MGFhMTZkNDExNDhmNmZlNGI1ODY2ZDNhNGUtMTc0NzE5OTM4Mg==`

### Estrutura dos Reels
- **5 segmentos**: Abertura → 3 Tópicos → Fechamento
- **Edição**: Cortes secos (sem transições)
- **Abertura padrão**: "E aí cambada! Olha eu aí de novo. Bora pras novas!"
- **Fechamento padrão**: Pausas entre enumerações + pausa longa antes "Sigo de olho"

### Método de Geração
1. **NUNCA tente usar API do HeyGen** (instável, retorna 404)
2. **SEMPRE use interface web**: https://app.heygen.com
3. **Upload manual** dos 5 áudios gerados
4. **Edição manual** juntando os vídeos

### Scripts Padrão
- `gerar_reel_renato_melhorado.py` - Gera os 5 áudios finais
- `limpar_outputs_manter_final.py` - Limpa outputs desnecessários  
- `instruções_heygen_final.py` - Mostra instruções para HeyGen
- `gerar_audio_completo.py` - **NOVO PADRÃO**: Gera áudio único do roteiro completo

## 🎯 PADRÃO FINAL APROVADO (06/01/2025)

### Estrutura de Pausas para Áudio Completo
- **5 quebras de linha** entre cada notícia (pausas longas)
- **3 quebras de linha** antes do "Sigo de olho" (pausa dramática)
- Este padrão foi testado e aprovado

### Comando Preferencial
```bash
python gerar_audio_completo.py  # Gera áudio único com todas as pausas corretas
```

### Avatar e Voice ID Atualizados
- **Voice ID**: `25NR0sM9ehsgXaoknsxO` (FlukakuFluido - ElevenLabs)
- **Avatar ID**: `3034bbd37f2540ddb70c90c7f67b4f5c` (HeyGen)
- **API Key HeyGen Atualizada**: `OTU2YjcxM2ZhZGY2NDE5Mjg3MzYzMmZlNjEyYjZiNzUtMTc0OTY5NDg0MQ==`