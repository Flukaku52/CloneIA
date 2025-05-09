#!/usr/bin/env python3
"""
Script para testar a geração de áudio com um script de desafio.
"""
import os
import logging
import time
from core.audio import AudioGenerator
from core.text import TextProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('test_desafio')

def main():
    """
    Função principal para testar a geração de áudio com um script de desafio.
    """
    # Script de desafio
    script = """E aí cambada, tô de volta na área e bora de Rapidinha! Mas dessa vez eu tenho um desafio pra vocês, tem algo "diferente" nesse vídeo, você consegue adivinhar o que? Bota aí nos comentários pra ver se você acerta, no fim do vídeo eu dou a resposta!"""
    
    # Inicializar o processador de texto
    text_processor = TextProcessor()
    print("Otimizando texto...")
    optimized_text = text_processor.optimize_for_speech(script)
    print(f"Texto otimizado: {optimized_text[:70]}...\n")
    
    # Inicializar o gerador de áudio com o perfil FlukakuFluido
    print("Inicializando gerador de áudio com perfil FlukakuFluido...")
    audio_generator = AudioGenerator(voice_profile="fluido")
    
    # Gerar nome de arquivo baseado em timestamp
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join("output", "audio", f"desafio_{timestamp}.mp3")
    
    # Gerar áudio
    print("Gerando áudio com a API do ElevenLabs...")
    audio_path = audio_generator.generate_audio(
        text=optimized_text,
        output_path=output_path,
        optimize=False  # Já otimizamos o texto acima
    )
    
    if audio_path:
        print(f"Áudio gerado com sucesso: {audio_path}")
        
        # Abrir o arquivo de áudio
        print("Abrindo o arquivo de áudio...")
        os.system(f"open {audio_path}")
        
        # Mostrar as configurações usadas
        print("\nConfigurações usadas:")
        import json
        print(json.dumps(audio_generator.voice_settings, indent=2))
    else:
        print("Falha ao gerar áudio.")

if __name__ == "__main__":
    main()
