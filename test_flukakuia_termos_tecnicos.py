#!/usr/bin/env python3
"""
Script para testar o perfil de voz FlukakuIA com termos técnicos de criptomoedas.
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
logger = logging.getLogger('test_flukakuia_tecnicos')

def main():
    """
    Função principal para testar o perfil de voz FlukakuIA com termos técnicos.
    """
    # Script com termos técnicos
    script = """E aí cambada! Tô de volta na área e bora de Rapidinha Cripto! 

Hoje vamos falar sobre alguns termos técnicos importantes no mundo das criptomoedas.

Primeiro, o que é staking? É quando você bloqueia suas criptos em uma carteira para ajudar a validar transações na rede e, em troca, recebe recompensas.

Já ouviu falar em DeFi? É a abreviação de Finanças Descentralizadas, um ecossistema de aplicativos financeiros que funcionam sem intermediários.

E o que são NFTs? São tokens não fungíveis, ou seja, ativos digitais únicos que representam a propriedade de algo, como uma obra de arte digital.

Por último, o que é um hard fork? É quando uma blockchain se divide em duas versões incompatíveis, criando uma nova criptomoeda.

E aí, você já conhecia esses termos? Deixa seu comentário e não esquece de dar aquele like! Até a próxima Rapidinha!"""
    
    # Inicializar o processador de texto
    text_processor = TextProcessor()
    print("Otimizando texto...")
    optimized_text = text_processor.optimize_for_speech(script)
    print(f"Texto otimizado: {optimized_text[:70]}...\n")
    
    # Inicializar o gerador de áudio com o perfil FlukakuIA
    print("Inicializando gerador de áudio com perfil FlukakuIA...")
    audio_generator = AudioGenerator(voice_profile="flukakuia")
    
    # Gerar nome de arquivo baseado em timestamp
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join("output", "audio", f"termos_flukakuia_{timestamp}.mp3")
    
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
