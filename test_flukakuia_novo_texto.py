#!/usr/bin/env python3
"""
Script para testar o perfil de voz FlukakuIA com um novo texto.
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
logger = logging.getLogger('test_flukakuia_novo')

def main():
    """
    Função principal para testar o perfil de voz FlukakuIA com um novo texto.
    """
    # Novo script para teste
    script = """E aí cambada! Tô de volta na área e bora de Rapidinha Cripto! 

Hoje vamos falar sobre o Bitcoin que tá bombando no mercado! Depois de uma queda forte, a moeda voltou com tudo e já tá valendo mais de 60 mil dólares! Isso é um sinal claro que o mercado tá se recuperando.

Outra notícia importante é sobre o Ethereum, que tá implementando uma atualização que vai reduzir as taxas de transação. Isso é ótimo pra quem usa a rede no dia a dia!

E aí, o que você achou dessas notícias? Deixa seu comentário e não esquece de dar aquele like! Até a próxima Rapidinha!"""
    
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
    output_path = os.path.join("output", "audio", f"bitcoin_flukakuia_{timestamp}.mp3")
    
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
