#!/usr/bin/env python3
"""
Script para concatenar vídeos do HeyGen mantendo a sincronização perfeita entre áudio e vídeo.
"""
import os
import sys
import logging
import argparse
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('concatenar_videos')

def criar_lista_videos(videos, lista_temp):
    """
    Cria um arquivo de lista para o FFmpeg.

    Args:
        videos: Lista de caminhos para os arquivos de vídeo
        lista_temp: Caminho para o arquivo de lista temporário

    Returns:
        bool: True se o arquivo foi criado com sucesso, False caso contrário
    """
    try:
        with open(lista_temp, 'w') as f:
            for video in videos:
                # Usar caminhos absolutos para evitar problemas
                video_abs = os.path.abspath(video)
                f.write(f"file '{video_abs}'\n")
        logger.info(f"Arquivo de lista criado: {lista_temp}")
        return True
    except Exception as e:
        logger.error(f"Erro ao criar arquivo de lista: {e}")
        return False

def concatenar_videos(videos, output_file=None):
    """
    Concatena vídeos do HeyGen mantendo a sincronização perfeita.

    Args:
        videos: Lista de caminhos para os arquivos de vídeo
        output_file: Caminho para o arquivo de saída (opcional)

    Returns:
        str: Caminho para o arquivo de saída ou None em caso de erro
    """
    # Verificar se os vídeos existem
    for video in videos:
        if not os.path.exists(video):
            logger.error(f"Vídeo não encontrado: {video}")
            return None

    # Criar diretório de saída se não existir
    if output_file:
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
    else:
        # Criar nome de arquivo padrão
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"output/videos/final/rapidinha_final_{timestamp}.mp4"
        output_dir = os.path.dirname(output_file)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    # Criar arquivo de lista temporário
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.txt', delete=False) as temp:
        lista_temp = temp.name

    # Criar lista de vídeos
    if not criar_lista_videos(videos, lista_temp):
        return None

    # Construir comando FFmpeg
    cmd = [
        'ffmpeg', '-y',
        '-f', 'concat',
        '-safe', '0',
        '-i', lista_temp,
        '-fflags', '+genpts',
        '-fps_mode', 'cfr',
        '-copyts',
        '-avoid_negative_ts', 'make_zero',
        '-c:v', 'libx264',
        '-profile:v', 'high',
        '-crf', '18',
        '-r', '30',
        '-pix_fmt', 'yuv420p',
        '-c:a', 'aac',
        '-ar', '48000',
        '-b:a', '192k',
        '-async', '1',
        '-movflags', '+faststart',
        output_file
    ]

    # Executar comando
    logger.info(f"Executando comando: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True)
        logger.info(f"Vídeos concatenados com sucesso: {output_file}")

        # Remover arquivo temporário
        os.unlink(lista_temp)

        return output_file
    except subprocess.CalledProcessError as e:
        logger.error(f"Erro ao concatenar vídeos: {e}")

        # Remover arquivo temporário
        os.unlink(lista_temp)

        return None

def main():
    """
    Função principal.
    """
    # Configurar argumentos da linha de comando
    parser = argparse.ArgumentParser(description="Concatenador de vídeos do HeyGen")
    parser.add_argument("--videos", nargs="+", help="Lista de caminhos para os arquivos de vídeo")
    parser.add_argument("--output", help="Caminho para o arquivo de saída")
    parser.add_argument("--timestamp", help="Timestamp dos vídeos a serem concatenados (formato: YYYYMMDD_HHMMSS)")
    parser.add_argument("--no-abrir", action="store_true", help="Não abrir o arquivo gerado")
    parser.add_argument("--debug", action="store_true", help="Ativar modo de depuração")

    args = parser.parse_args()

    # Configurar nível de log
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    # Encontrar vídeos
    if args.videos:
        videos = args.videos
    elif args.timestamp:
        # Encontrar vídeos com o timestamp fornecido
        import glob
        videos = sorted(glob.glob(f"output/videos/rapidinha_video_secao_*_{args.timestamp}*.mp4"))
        if not videos:
            logger.error(f"Nenhum vídeo encontrado com o timestamp: {args.timestamp}")
            return 1
        logger.info(f"Vídeos encontrados: {len(videos)}")
        for video in videos:
            logger.info(f"  - {video}")
    else:
        # Encontrar os vídeos mais recentes
        import glob

        # Encontrar os vídeos mais recentes
        video_files = sorted(glob.glob("output/videos/rapidinha_video_secao_*.mp4"), key=os.path.getmtime, reverse=True)

        if not video_files:
            logger.error("Nenhum arquivo de vídeo encontrado.")
            return 1

        # Agrupar vídeos pelo timestamp
        from collections import defaultdict
        videos_por_timestamp = defaultdict(list)

        for video in video_files:
            # Extrair o timestamp do nome do arquivo
            try:
                timestamp = os.path.basename(video).split("_")[-1].split(".")[0]
                videos_por_timestamp[timestamp].append(video)
            except (IndexError, ValueError):
                continue

        # Usar o grupo com mais vídeos
        if not videos_por_timestamp:
            logger.error("Não foi possível agrupar os vídeos por timestamp.")
            return 1

        timestamp, videos = max(videos_por_timestamp.items(), key=lambda x: len(x[1]))

        # Ordenar por número de seção
        videos = sorted(videos, key=lambda x: int(os.path.basename(x).split("_")[3]))

        logger.info(f"Usando os vídeos do timestamp {timestamp}:")
        for video in videos:
            logger.info(f"  - {video}")

    # Concatenar vídeos
    output_file = concatenar_videos(videos, args.output)

    if output_file:
        logger.info(f"Vídeo final gerado: {output_file}")

        # Abrir arquivo gerado
        if not args.no_abrir:
            if sys.platform == "darwin":
                subprocess.run(["open", output_file])
            elif sys.platform == "win32":
                os.startfile(output_file)
            elif sys.platform == "linux":
                subprocess.run(["xdg-open", output_file])
    else:
        logger.error("Falha ao concatenar vídeos.")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
