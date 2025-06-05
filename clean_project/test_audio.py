#!/usr/bin/env python3
"""
Script para testar a geração de áudio com a versão limpa do projeto.
"""
import os
import logging
import argparse
from core.audio import AudioGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('test_audio')

def main():
    """
    Função principal para testar a geração de áudio.
    """
    parser = argparse.ArgumentParser(description="Teste de geração de áudio")
    parser.add_argument("--text", help="Texto para gerar áudio")
    parser.add_argument("--voice-profile", help="Perfil de voz a ser usado")
    parser.add_argument("--dry-run", action="store_true", help="Simular a geração sem fazer chamadas de API")
    
    args = parser.parse_args()
    
    # Texto padrão se não for fornecido
    text = args.text
    if not text:
        text = """
        E aí cambada! Tô de volta na área e bora de Rapidinha! Hoje vamos falar sobre as últimas novidades do mundo cripto.
        
        O Bitcoin continua bombando e atingiu um novo recorde de preço, chegando a mais de 60 mil dólares!
        
        E aí, o que você achou dessas notícias? Deixa seu comentário e não esquece de dar aquele like!
        """
    
    # Criar instância do gerador de áudio
    audio_generator = AudioGenerator(voice_profile=args.voice_profile)
    
    # Gerar áudio
    logger.info(f"Gerando áudio para o texto: {text[:50]}...")
    audio_path = audio_generator.generate_audio(
        text=text,
        dry_run=args.dry_run
    )
    
    if audio_path:
        logger.info(f"Áudio gerado com sucesso: {audio_path}")
    else:
        logger.error("Falha ao gerar áudio.")

if __name__ == "__main__":
    main()
