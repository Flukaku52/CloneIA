#!/usr/bin/env python3
"""
Script para gerar áudio usando o perfil FlukakuIA.
"""
import os
import argparse
import logging
from core.audio import AudioGenerator
from core.utils import ensure_directory, get_timestamp_filename, OUTPUT_DIR

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('gerar_audio')

def generate_audio(script_path: str, output_path: str = None, profile_name: str = "flukakuia"):
    """
    Gera áudio a partir de um script usando o perfil especificado.
    
    Args:
        script_path: Caminho para o arquivo de script
        output_path: Caminho para salvar o áudio (se None, gera um nome baseado no timestamp)
        profile_name: Nome do perfil de voz a ser usado
        
    Returns:
        str: Caminho para o áudio gerado, ou None se falhar
    """
    if not os.path.exists(script_path):
        logger.error(f"Arquivo de script não encontrado: {script_path}")
        return None
    
    # Carregar o texto do script
    with open(script_path, 'r', encoding='utf-8') as f:
        script_content = f.read()
    
    # Criar o gerador de áudio
    audio_generator = AudioGenerator(voice_profile=profile_name)
    
    # Definir o caminho para o áudio de saída
    if not output_path:
        timestamp = get_timestamp_filename("audio", "mp3")
        output_path = os.path.join(OUTPUT_DIR, "audio", timestamp)
    
    # Garantir que o diretório existe
    ensure_directory(os.path.dirname(output_path))
    
    # Gerar o áudio
    logger.info(f"Gerando áudio com o perfil {profile_name}...")
    
    audio_result = audio_generator.generate_audio(
        script_content, output_path, optimize=True
    )
    
    if audio_result:
        logger.info(f"Áudio gerado com sucesso: {audio_result}")
        return audio_result
    else:
        logger.error("Falha ao gerar o áudio")
        return None

def main():
    parser = argparse.ArgumentParser(description="Gerador de áudio para o CloneIA")
    parser.add_argument("--script", required=True, help="Caminho para o arquivo de script")
    parser.add_argument("--output", help="Caminho para salvar o áudio")
    parser.add_argument("--profile", default="flukakuia", help="Nome do perfil de voz a ser usado")
    
    args = parser.parse_args()
    
    # Gerar o áudio
    audio_path = generate_audio(
        script_path=args.script,
        output_path=args.output,
        profile_name=args.profile
    )
    
    # Retornar o caminho do áudio para uso em outros scripts
    if audio_path:
        print(f"AUDIO_PATH={audio_path}")

if __name__ == "__main__":
    main()
