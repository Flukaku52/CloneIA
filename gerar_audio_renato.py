#!/usr/bin/env python3
"""
Script para gerar áudio do roteiro personalizado do Renato
"""

import os
import sys
import logging
from pathlib import Path

# Adiciona o diretório do projeto ao path
project_root = Path(__file__).parent.resolve()
sys.path.insert(0, str(project_root))

from core.audio import AudioGenerator

# Configura logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    
    # Lê o script
    script_path = project_root / "scripts" / "renato_connecticut_bitcoin.txt"
    with open(script_path, 'r', encoding='utf-8') as f:
        texto = f.read()
    
    print("🎙️ GERANDO ÁUDIO DO ROTEIRO PERSONALIZADO")
    print("=" * 60)
    
    # Inicializa o gerador de áudio
    audio_gen = AudioGenerator()
    
    # Gera o áudio
    output_dir = project_root / "output" / "audio"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    audio_path = output_dir / "renato_connecticut_bitcoin_audio.mp3"
    
    print(f"📝 Texto: {len(texto)} caracteres")
    print(f"🎤 Voz: {audio_gen.voice_name} (ID: {audio_gen.voice_id})")
    print(f"📁 Salvando em: {audio_path}")
    print("🔄 Gerando áudio...")
    
    success = audio_gen.generate_audio(texto, str(audio_path))
    
    if success:
        print(f"✅ Áudio gerado com sucesso!")
        print(f"📂 Arquivo: {audio_path}")
        
        # Mostra duração estimada
        chars = len(texto)
        estimated_duration = chars / 150 * 60  # ~150 chars por minuto
        print(f"⏱️ Duração estimada: {estimated_duration:.1f} segundos")
    else:
        print("❌ Erro ao gerar áudio")
        return 1
    
    print("\n🎯 PRÓXIMOS PASSOS:")
    print("1. Use o áudio no HeyGen para gerar o vídeo com avatar")
    print("2. Ou use: python generate_reel_correto.py com o script customizado")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())