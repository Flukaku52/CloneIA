#!/usr/bin/env python3
"""
Script para sincronizar vídeo e áudio com precisão.
"""
import os
import sys
import logging
import argparse
import subprocess
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('sincronizar_video')

def sincronizar_video(video_file, audio_file, output_file, audio_offset=0.0):
    """
    Sincroniza um vídeo com um arquivo de áudio.
    
    Args:
        video_file: Caminho para o arquivo de vídeo
        audio_file: Caminho para o arquivo de áudio
        output_file: Caminho para o arquivo de saída
        audio_offset: Deslocamento do áudio em segundos (positivo = atraso, negativo = adiantamento)
    
    Returns:
        bool: True se o vídeo foi sincronizado com sucesso, False caso contrário
    """
    # Criar diretório de saída se não existir
    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Construir comando FFmpeg
    if audio_offset >= 0:
        # Atrasar o áudio
        cmd = [
            'ffmpeg', '-y',
            '-i', video_file,
            '-i', audio_file,
            '-c:v', 'copy',
            '-filter_complex', f'[1:a]adelay={int(audio_offset * 1000)}|{int(audio_offset * 1000)}[a]',
            '-map', '0:v',
            '-map', '[a]',
            '-c:a', 'aac',
            output_file
        ]
    else:
        # Adiantar o áudio (atrasar o vídeo)
        cmd = [
            'ffmpeg', '-y',
            '-i', video_file,
            '-i', audio_file,
            '-filter_complex', f'[0:v]setpts=PTS+{abs(audio_offset)}/TB[v]',
            '-map', '[v]',
            '-map', '1:a',
            '-c:v', 'libx264',
            '-c:a', 'aac',
            output_file
        ]
    
    # Executar comando
    logger.info(f"Executando comando: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True)
        logger.info(f"Vídeo sincronizado com sucesso: {output_file}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Erro ao sincronizar vídeo: {e}")
        return False

def combinar_videos(video_files, output_file, transition='fade', transition_duration=0.5):
    """
    Combina vários vídeos em um único arquivo.
    
    Args:
        video_files: Lista de caminhos para os arquivos de vídeo
        output_file: Caminho para o arquivo de saída
        transition: Tipo de transição entre os vídeos
        transition_duration: Duração da transição em segundos
    
    Returns:
        bool: True se os vídeos foram combinados com sucesso, False caso contrário
    """
    # Criar diretório de saída se não existir
    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Construir comando FFmpeg
    cmd = ['ffmpeg', '-y']
    
    # Adicionar entradas
    for video_file in video_files:
        cmd.extend(['-i', video_file])
    
    # Construir filtro complexo
    filter_complex = []
    
    # Escalar vídeos
    for i in range(len(video_files)):
        filter_complex.append(f'[{i}:v]scale=720:1280,setsar=1[v{i}]')
    
    # Aplicar transições
    for i in range(len(video_files) - 1):
        if i == 0:
            filter_complex.append(f'[v{i}][v{i+1}]xfade=transition={transition}:duration={transition_duration}:offset=3[v{i+1}_t]')
        else:
            filter_complex.append(f'[v{i}_t][v{i+1}]xfade=transition={transition}:duration={transition_duration}:offset=3[v{i+1}_t]')
    
    # Concatenar áudios
    audio_inputs = []
    for i in range(len(video_files)):
        audio_inputs.append(f'[{i}:a]')
    
    filter_complex.append(f'{"".join(audio_inputs)}concat=n={len(video_files)}:v=0:a=1[aout]')
    
    # Adicionar filtro complexo ao comando
    cmd.extend(['-filter_complex', ';'.join(filter_complex)])
    
    # Mapear saídas
    cmd.extend([
        '-map', f'[v{len(video_files)-1}_t]',
        '-map', '[aout]',
        '-c:v', 'libx264',
        '-c:a', 'aac',
        '-preset', 'medium',
        '-crf', '23',
        output_file
    ])
    
    # Executar comando
    logger.info(f"Executando comando: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True)
        logger.info(f"Vídeos combinados com sucesso: {output_file}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Erro ao combinar vídeos: {e}")
        return False

def main():
    """
    Função principal.
    """
    # Configurar argumentos da linha de comando
    parser = argparse.ArgumentParser(description="Sincronizador de vídeo e áudio")
    parser.add_argument("--video", help="Caminho para o arquivo de vídeo")
    parser.add_argument("--audio", help="Caminho para o arquivo de áudio")
    parser.add_argument("--output", help="Caminho para o arquivo de saída")
    parser.add_argument("--offset", type=float, default=0.0, help="Deslocamento do áudio em segundos (positivo = atraso, negativo = adiantamento)")
    parser.add_argument("--combinar", action="store_true", help="Combinar vídeos sincronizados")
    parser.add_argument("--videos", nargs="+", help="Lista de caminhos para os arquivos de vídeo a serem combinados")
    parser.add_argument("--debug", action="store_true", help="Ativar modo de depuração")

    args = parser.parse_args()

    # Configurar nível de log
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    # Verificar argumentos
    if args.combinar:
        if not args.videos:
            logger.error("Nenhum vídeo fornecido para combinar.")
            return 1
        
        if not args.output:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            args.output = f"output/videos/final/rapidinha_final_{timestamp}.mp4"
        
        # Combinar vídeos
        if combinar_videos(args.videos, args.output):
            # Abrir arquivo gerado
            if sys.platform == "darwin":
                subprocess.run(["open", args.output])
            elif sys.platform == "win32":
                os.startfile(args.output)
            elif sys.platform == "linux":
                subprocess.run(["xdg-open", args.output])
        else:
            logger.error("Falha ao combinar vídeos.")
            return 1
    else:
        if not args.video or not args.audio:
            logger.error("Vídeo e áudio são obrigatórios.")
            return 1
        
        if not args.output:
            base_name = os.path.splitext(os.path.basename(args.video))[0]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            args.output = f"output/videos/sync/{base_name}_sync_{timestamp}.mp4"
        
        # Sincronizar vídeo
        if sincronizar_video(args.video, args.audio, args.output, args.offset):
            # Abrir arquivo gerado
            if sys.platform == "darwin":
                subprocess.run(["open", args.output])
            elif sys.platform == "win32":
                os.startfile(args.output)
            elif sys.platform == "linux":
                subprocess.run(["xdg-open", args.output])
        else:
            logger.error("Falha ao sincronizar vídeo.")
            return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
