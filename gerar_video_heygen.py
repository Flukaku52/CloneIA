#!/usr/bin/env python3
"""
Script para gerar vídeo no HeyGen usando áudio gerado com o ElevenLabs.
"""
import os
import argparse
import logging
from heygen_video_generator import HeyGenVideoGenerator
from core.utils import ensure_directory, get_timestamp_filename, OUTPUT_DIR

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('gerar_video_heygen')

def generate_heygen_video(audio_path: str, script_path: str = None, output_path: str = None,
                         avatar_id: str = None, folder_name: str = "augment"):
    """
    Gera um vídeo no HeyGen usando um arquivo de áudio.

    Args:
        audio_path: Caminho para o arquivo de áudio
        script_path: Caminho para o arquivo de script (opcional, para fallback)
        output_path: Caminho para salvar o vídeo (se None, gera um nome baseado no timestamp)
        avatar_id: ID do avatar a ser usado (se None, usa o avatar configurado)
        folder_name: Nome da pasta no HeyGen onde o vídeo será salvo

    Returns:
        str: Caminho para o vídeo gerado, ou None se falhar
    """
    if not os.path.exists(audio_path):
        logger.error(f"Arquivo de áudio não encontrado: {audio_path}")
        return None

    # Carregar o texto do script (para fallback)
    script_content = ""
    if script_path and os.path.exists(script_path):
        with open(script_path, 'r', encoding='utf-8') as f:
            script_content = f.read()

    # Criar o gerador de vídeo do HeyGen
    heygen_generator = HeyGenVideoGenerator()

    # Definir o ID do avatar se fornecido
    if avatar_id:
        heygen_generator.avatar_id = avatar_id
        logger.info(f"Usando avatar com ID: {avatar_id}")

    # Definir o caminho para o vídeo de saída
    if not output_path:
        timestamp = get_timestamp_filename("heygen", "mp4")
        output_path = os.path.join(OUTPUT_DIR, "videos", timestamp)

    # Garantir que o diretório existe
    ensure_directory(os.path.dirname(output_path))

    # Gerar o vídeo
    logger.info("Gerando vídeo com o HeyGen...")

    video_result = heygen_generator.generate_video(
        script=script_content,  # Texto para fallback, caso o áudio falhe
        audio_path=audio_path,  # Usar o áudio gerado
        output_path=output_path,
        folder_name=folder_name  # Salvar na pasta especificada do HeyGen
    )

    if video_result:
        logger.info(f"Vídeo gerado com sucesso: {video_result}")
        return video_result
    else:
        logger.error("Falha ao gerar o vídeo")
        return None

def main():
    parser = argparse.ArgumentParser(description="Gerador de vídeo HeyGen para o CloneIA")
    parser.add_argument("--audio", help="Caminho para o arquivo de áudio")
    parser.add_argument("--script", help="Caminho para o arquivo de script (opcional)")
    parser.add_argument("--output", help="Caminho para salvar o vídeo")
    parser.add_argument("--avatar", default="189d9626f12f473f8f6e927c5ec482fa",
                      help="ID do avatar a ser usado (padrão: Flukaku Rapidinha)")
    parser.add_argument("--folder", default="augment",
                      help="Nome da pasta no HeyGen onde o vídeo será salvo (padrão: augment)")

    args = parser.parse_args()

    # Usar o áudio fornecido ou o padrão
    audio_path = args.audio
    if not audio_path:
        audio_path = os.path.join(OUTPUT_DIR, 'audio', 'desafio_flukakuia.mp3')

    # Gerar o vídeo
    generate_heygen_video(
        audio_path=audio_path,
        script_path=args.script,
        output_path=args.output,
        avatar_id=args.avatar,
        folder_name=args.folder
    )

if __name__ == "__main__":
    main()
