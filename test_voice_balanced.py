#!/usr/bin/env python3
"""
Teste com configuração balanceada e processamento de texto otimizado
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Adiciona o diretório do projeto ao path
sys.path.append(str(Path(__file__).parent))

from core.audio import AudioGenerator
from core.utils import load_voice_config

def optimize_text_for_natural_pauses(text: str) -> str:
    """
    Otimização específica para evitar pausas artificiais
    """
    if not text:
        return text
    
    # Preserva "Fala cambada" natural
    if text.lower().startswith("fala cambada"):
        text = "Fala cambada" + text[len("fala cambada"):]
    
    # Remove pontuações que criam pausas artificiais excessivas
    # MAS mantém algumas para respiração natural
    text = text.replace('...', ' ')  # Remove ellipses
    text = text.replace(';;', ' ')   # Remove ponto e vírgula duplo
    text = text.replace('  ', ' ')   # Remove espaços duplos
    
    # Mantém vírgulas e pontos para pausas naturais leves
    # (diferente das versões anteriores que removiam tudo)
    
    # Termos cripto com pronúncia natural
    replacements = {
        "BTC": "Bitcoin",  # Mais natural que "BêTêCê"
        "supply": "fornecimento",
        "MicroStrategy": "Micro Strategy"
    }
    
    for original, replacement in replacements.items():
        text = text.replace(original, replacement)
    
    return text

def test_balanced_voice():
    # Script de teste
    script = """Fala cambada! Tô de volta por aqui e bora pras notícias.

Empresas já têm mais de 3% do supply de BTC

Seguinte: segundo o banco Standard Chartered, 61 empresas que têm ações em bolsa já acumulam 3,2% de todo o Bitcoin que vai existir no mundo.

Entre elas estão MicroStrategy, Tesla e outras gigantes que tão comprando BTC pra colocar em caixa, como reserva de valor.

Em vez de só dólar ou ouro, agora tem empresa diversificando com Bitcoin.
Isso reforça que o BTC não é mais só papo de investidor de rede social — tá virando um ativo institucional."""

    print("🎙️ Teste com Configuração Balanceada")
    print("=" * 50)
    print("📝 Script:")
    print("-" * 30)
    print(script)
    print("-" * 30)
    
    # Carrega configuração balanceada
    voice_config = load_voice_config("balanced")
    print(f"\n🔧 Configuração Balanceada:")
    print(f"   - Stability: {voice_config['settings']['stability']} (meio-termo)")
    print(f"   - Similarity: {voice_config['settings']['similarity_boost']} (equilibrado)")
    print(f"   - Style: {voice_config['settings']['style']} (natural)")
    
    # Otimiza texto para pausas naturais
    optimized_script = optimize_text_for_natural_pauses(script)
    print(f"\n📋 Ajustes no texto:")
    print(f"   - Removidas pausas artificiais excessivas")
    print(f"   - Mantidas vírgulas/pontos para respiração natural")
    print(f"   - Termos cripto mais naturais")
    
    # Gera áudio
    audio_gen = AudioGenerator()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"output/audio/teste_balanced_{timestamp}.mp3"
    
    print(f"\n🎵 Gerando áudio balanceado...")
    try:
        audio_path = audio_gen.generate_audio(optimized_script, output_path)
        
        if audio_path and os.path.exists(audio_path):
            file_size = os.path.getsize(audio_path) / 1024
            print(f"\n✅ Áudio balanceado gerado!")
            print(f"📁 Arquivo: {audio_path}")
            print(f"📊 Tamanho: {file_size:.1f} KB")
            
            print(f"\n🎯 OBJETIVO DESTA VERSÃO:")
            print(f"   ✅ Ritmo relaxado (sem pressa)")
            print(f"   ✅ Pausas naturais (não artificiais)")
            print(f"   ✅ Energia variada (não robótica)")
            print(f"   ✅ Fluidez conversacional")
            
            print(f"\n🎧 Escute e compare com seus benchmarks!")
            
        else:
            print("❌ Erro na geração")
            
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    test_balanced_voice()