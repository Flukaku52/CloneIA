#!/usr/bin/env python3
"""
Script para testar a geração de áudio com saudação mais entusiasmada
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Adiciona o diretório do projeto ao path
sys.path.append(str(Path(__file__).parent))

from core.audio import AudioGenerator
from core.utils import load_voice_config

def custom_optimize_text(text: str) -> str:
    """
    Otimização customizada para deixar o "Fala cambada" mais entusiasmado
    """
    if not text:
        return text
    
    # Tratamento especial para "Fala cambada" - com mais energia
    if text.lower().startswith("fala cambada"):
        # Adiciona ênfase e velocidade
        text = "FALA CAMBADAAA!" + text[len("fala cambada"):]
    
    # Remove pontuações que causam pausas
    text = text.replace(',', '').replace('.', '').replace('!', '').replace('?', '')
    
    # Termos cripto
    replacements = {
        "Bitcoin": "Bitcoim",
        "BTC": "BêTêCê",
        "supply": "suplái",
        "MicroStrategy": "MáicroStrategy",
        "Tesla": "Tésla"
    }
    
    for original, replacement in replacements.items():
        text = text.replace(original, replacement)
    
    return text

def test_voice_generation():
    # Script fornecido pelo usuário
    script = """Fala cambada! Tô de volta por aqui e bora pras notícias.

Empresas já têm mais de 3% do supply de BTC

Seguinte: segundo o banco Standard Chartered, 61 empresas que têm ações em bolsa já acumulam 3,2% de todo o Bitcoin que vai existir no mundo.

Entre elas estão MicroStrategy, Tesla e outras gigantes que tão comprando BTC pra colocar em caixa, como reserva de valor.

Em vez de só dólar ou ouro, agora tem empresa diversificando com Bitcoin.
Isso reforça que o BTC não é mais só papo de investidor de rede social — tá virando um ativo institucional."""

    print("🎙️ Iniciando teste de geração de áudio com saudação entusiasmada...")
    print("📝 Script a ser convertido:")
    print("-" * 50)
    print(script)
    print("-" * 50)
    
    # Carrega configuração de voz otimizada por ML
    voice_config = load_voice_config("ml_optimized")
    
    # Ajusta para mais energia na saudação
    voice_config['settings']['stability'] = 0.05  # Ainda menos estabilidade para mais variação
    voice_config['settings']['style'] = 0.9      # Mais estilo para energia
    
    print(f"\n🔧 Usando perfil de voz ajustado para entusiasmo:")
    print(f"   - Voice ID: {voice_config.get('voice_id')}")
    print(f"   - Stability: {voice_config['settings']['stability']} (reduzido para mais energia)")
    print(f"   - Similarity Boost: {voice_config['settings']['similarity_boost']}")
    print(f"   - Style: {voice_config['settings']['style']} (aumentado para mais entusiasmo)")
    
    # Aplica otimização customizada
    optimized_script = custom_optimize_text(script)
    print(f"\n📋 Script otimizado:")
    print(optimized_script[:100] + "...")
    
    # Inicializa gerador de áudio
    audio_gen = AudioGenerator()
    
    # Gera timestamp para o arquivo
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"output/audio/teste_voz_entusiasmado_{timestamp}.mp3"
    
    print(f"\n🎵 Gerando áudio com saudação entusiasmada...")
    try:
        # Gera o áudio com script otimizado
        audio_path = audio_gen.generate_audio(optimized_script, output_path)
        
        if audio_path and os.path.exists(audio_path):
            file_size = os.path.getsize(audio_path) / 1024  # KB
            print(f"\n✅ Áudio gerado com sucesso!")
            print(f"📁 Arquivo salvo em: {audio_path}")
            print(f"📊 Tamanho do arquivo: {file_size:.2f} KB")
            print(f"\n🎧 O 'Fala cambada' deve estar mais rápido e entusiasmado agora!")
        else:
            print("\n❌ Erro ao gerar o áudio. Verifique as configurações.")
            
    except Exception as e:
        print(f"\n❌ Erro durante a geração: {str(e)}")

if __name__ == "__main__":
    test_voice_generation()