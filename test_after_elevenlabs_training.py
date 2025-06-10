#!/usr/bin/env python3
"""
Script para testar depois que você upar os samples no ElevenLabs
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Adiciona o diretório do projeto ao path
sys.path.append(str(Path(__file__).parent))

from core.audio import AudioGenerator
from core.utils import load_voice_config

def test_after_elevenlabs_update():
    # Script de teste
    script = """Fala cambada! Tô de volta por aqui e bora pras notícias.

Empresas já têm mais de 3% do supply de BTC.

Seguinte: segundo o banco Standard Chartered, 61 empresas que têm ações em bolsa já acumulam 3,2% de todo o Bitcoin que vai existir no mundo.

Entre elas estão MicroStrategy, Tesla e outras gigantes que tão comprando BTC pra colocar em caixa, como reserva de valor."""

    print("🎙️ TESTE APÓS TREINAMENTO NO ELEVENLABS")
    print("=" * 55)
    print("📝 Script de teste:")
    print("-" * 30)
    print(script)
    print("-" * 30)
    
    # Carrega configuração direta do ElevenLabs
    voice_config = load_voice_config("elevenlabs_direct")
    print(f"\n🔧 Configuração ElevenLabs Direct:")
    print(f"   - Voice ID: {voice_config.get('voice_id')}")
    print(f"   - Stability: {voice_config['settings']['stability']}")
    print(f"   - Similarity: {voice_config['settings']['similarity_boost']}")
    print(f"   - Style: {voice_config['settings']['style']}")
    
    # Gera áudio
    audio_gen = AudioGenerator()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"output/audio/teste_pos_training_{timestamp}.mp3"
    
    print(f"\n🎵 Gerando áudio com novo treinamento...")
    print(f"💡 Este teste vai mostrar se os novos samples melhoraram a qualidade!")
    
    try:
        audio_path = audio_gen.generate_audio(script, output_path)
        
        if audio_path and os.path.exists(audio_path):
            file_size = os.path.getsize(audio_path) / 1024
            print(f"\n✅ Áudio gerado com novo treinamento!")
            print(f"📁 Arquivo: {audio_path}")
            print(f"📊 Tamanho: {file_size:.1f} KB")
            
            print(f"\n🎯 AGORA COMPARE:")
            print(f"   🔄 Este novo áudio")
            print(f"   🆚 Suas gravações originais")
            print(f"   📈 Deve estar muito melhor!")
            
            print(f"\n💬 AVALIE:")
            print(f"   • Naturalidade da voz")
            print(f"   • Ritmo e pausas")
            print(f"   • Similaridade com seu timbre")
            print(f"   • Qualidade geral")
            
        else:
            print("❌ Erro na geração")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    test_after_elevenlabs_update()