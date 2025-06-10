#!/usr/bin/env python3
"""
Teste direto com o novo Voice ID
"""

import os
import sys
import requests
import json
from pathlib import Path
from datetime import datetime

# Adiciona o diretório do projeto ao path
sys.path.append(str(Path(__file__).parent))

from core.utils import load_elevenlabs_api_key

def test_new_voice_direct():
    """
    Teste direto com o novo Voice ID
    """
    
    # Novo Voice ID
    NEW_VOICE_ID = "25NR0sM9ehsgXaoknsxO"
    
    # Script de teste
    script = """Fala cambada! Tô de volta por aqui e bora pras notícias.

Empresas já têm mais de 3% do supply de Bitcoin.

Seguinte: segundo o banco Standard Chartered, 61 empresas que têm ações em bolsa já acumulam 3,2% de todo o Bitcoin que vai existir no mundo."""

    print("🎙️ TESTE DIRETO COM NOVO VOICE ID")
    print("=" * 50)
    print(f"🆔 Voice ID: {NEW_VOICE_ID}")
    print("📝 Script:")
    print("-" * 30)
    print(script)
    print("-" * 30)

    # Carrega API key
    api_key = load_elevenlabs_api_key()
    if not api_key:
        print("❌ API Key não encontrada")
        return

    # Configurações de voz
    voice_settings = {
        "stability": 0.3,
        "similarity_boost": 0.7,
        "style": 0.8,
        "use_speaker_boost": True
    }

    print(f"\n🔧 Configurações:")
    print(f"   - Stability: {voice_settings['stability']}")
    print(f"   - Similarity: {voice_settings['similarity_boost']}")
    print(f"   - Style: {voice_settings['style']}")

    # Prepara requisição
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{NEW_VOICE_ID}"
    
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key
    }
    
    data = {
        "text": script,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": voice_settings
    }

    print(f"\n🎵 Gerando áudio com novo Voice ID...")
    
    try:
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 200:
            # Salva áudio
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"output/audio/teste_novo_voice_{timestamp}.mp3"
            
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            file_size = len(response.content) / 1024
            
            print(f"\n✅ Áudio gerado com sucesso!")
            print(f"📁 Arquivo: {output_path}")
            print(f"📊 Tamanho: {file_size:.1f} KB")
            
            print(f"\n🎯 NOVO PERFIL TESTADO!")
            print(f"   🎧 Escute e compare com o anterior")
            print(f"   📈 Deve ter melhorado significativamente")
            
        else:
            print(f"❌ Erro na API: {response.status_code}")
            print(f"   Response: {response.text}")
            
            if response.status_code == 404:
                print("   💡 Voice ID pode não existir ou não estar acessível")
            elif response.status_code == 401:
                print("   💡 Problema com API Key")
                
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")

if __name__ == "__main__":
    test_new_voice_direct()