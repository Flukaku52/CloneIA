# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CloneIA is an AI-powered content generation system for creating "Rapidinha no Cripto" (Quick Crypto Updates) videos. It generates complete crypto news content by:
- Cloning the presenter's voice using ElevenLabs API
- Creating AI avatar videos using HeyGen API
- Generating scripts that mimic the presenter's communication style
- Processing crypto news from various APIs

## Key Commands

### Setup and Dependencies
```bash
# Install Python dependencies
pip install -r requirements.txt

# Run initial setup (creates directories and .env template)
python setup.py

# Install Node dependencies (for ElevenLabs)
npm install
```

### Video Generation Commands
```bash
# Generate complete video with optimized generator (RECOMMENDED)
python rapidinha_generator_optimized.py --script "Your script here"

# Test HeyGen video generation
python test_optimized_generator.py --generate

# List available HeyGen avatars
python test_optimized_generator.py --list-avatars

# Generate video using specific config
export HEYGEN_API_KEY="your_key" && export ELEVENLABS_API_KEY="your_key" && python generate_reel_correto.py
```

### Audio Generation
```bash
# Extract audio samples from reference videos
python audio_generator.py --extract

# Clone voice using extracted samples
python audio_generator.py --clone

# Generate audio from text
python audio_generator.py --text "Text to convert to speech"
```

### Testing
```bash
# Test first segment of video
python test_primeiro_segmento.py

# Test audio generation
python test_audio.py
```

## Architecture Overview

### Core Modules (`core/`)
- **audio.py**: Handles ElevenLabs API integration for voice cloning and audio generation
- **video.py**: Creates videos using MoviePy (intro animations, text overlays, transitions)
- **text.py**: Processes and optimizes text for natural speech synthesis
- **utils.py**: API key management, file handling, directory operations

### Configuration System
The project uses multiple JSON configuration files in `config/`:
- **avatar_config.json**: HeyGen avatar IDs and profiles
- **voice_config_*.json**: Different voice profiles with ElevenLabs parameters (stability, similarity_boost, style)
- **heygen_profiles.json**: Multiple HeyGen API accounts with different quotas
- **configuracoes_padrao_sistema.json**: System-wide defaults

### API Integration Flow
1. **Content Generation**: Scripts generated using OpenAI API or mock data
2. **Audio Creation**: Text → ElevenLabs API → Audio file
3. **Video Generation**: 
   - Simple: MoviePy creates video with static image + audio
   - Advanced: HeyGen API creates AI avatar video with synchronized speech

### Working with Voice Profiles
The system supports multiple voice configurations for different effects:
- "fluido": Natural flowing speech (stability: 0.2, similarity_boost: 0.7)
- "carioca_fluido": Regional accent variation
- "ultra_natural": Maximum naturalness settings

Always check `config/voice_config_*.json` before modifying voice parameters.

### HeyGen Avatar Management
- Avatar IDs are stored in `config/avatar_config.json`
- Multiple profiles in `config/heygen_profiles.json` allow switching between accounts
- Use `test_optimized_generator.py --list-avatars` to verify available avatars

## Important Notes

- **API Keys**: All API keys must be set in `.env` file (OpenAI, ElevenLabs, HeyGen, CryptoCompare, NewsAPI)
- **Voice Samples**: Store in `reference/voice_samples/` (7-12 seconds each, 20-40 samples for best results)
- **Output Structure**: Generated content goes to `output/audio/` and `output/videos/`
- **Current Production Config**: Using HeyGen Profile 2 with avatar "flukakudabet" (ID: bd9548bed4984738a93b0db0c6c3edc9)