#!/usr/bin/env python3
"""
Script para analisar vídeos de referência e extrair informações para machine learning.
"""
import os
import sys
import json
import logging
import argparse
import subprocess
from datetime import datetime
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('analisar_videos')

def extrair_info_video(video_path):
    """
    Extrai informações básicas do vídeo usando ffprobe.
    
    Args:
        video_path: Caminho para o arquivo de vídeo
        
    Returns:
        dict: Informações do vídeo ou None em caso de erro
    """
    try:
        # Comando para extrair informações do vídeo
        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            video_path
        ]
        
        # Executar comando
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # Converter saída para JSON
        info = json.loads(result.stdout)
        
        # Extrair informações relevantes
        video_info = {
            'filename': os.path.basename(video_path),
            'path': video_path,
            'size_bytes': int(info['format'].get('size', 0)),
            'duration_seconds': float(info['format'].get('duration', 0)),
            'bitrate': int(info['format'].get('bit_rate', 0)),
            'format': info['format'].get('format_name', ''),
            'analyzed_at': datetime.now().isoformat()
        }
        
        # Extrair informações dos streams
        for stream in info.get('streams', []):
            if stream.get('codec_type') == 'video':
                video_info['video_codec'] = stream.get('codec_name', '')
                video_info['width'] = stream.get('width', 0)
                video_info['height'] = stream.get('height', 0)
                video_info['fps'] = eval(stream.get('r_frame_rate', '0/1'))
            elif stream.get('codec_type') == 'audio':
                video_info['audio_codec'] = stream.get('codec_name', '')
                video_info['audio_channels'] = stream.get('channels', 0)
                video_info['audio_sample_rate'] = stream.get('sample_rate', '')
        
        return video_info
    
    except Exception as e:
        logger.error(f"Erro ao extrair informações do vídeo {video_path}: {e}")
        return None

def extrair_frames(video_path, output_dir, num_frames=10):
    """
    Extrai frames do vídeo para análise.
    
    Args:
        video_path: Caminho para o arquivo de vídeo
        output_dir: Diretório de saída para os frames
        num_frames: Número de frames a extrair
        
    Returns:
        list: Lista de caminhos para os frames extraídos ou None em caso de erro
    """
    try:
        # Criar diretório de saída
        os.makedirs(output_dir, exist_ok=True)
        
        # Obter duração do vídeo
        info = extrair_info_video(video_path)
        if not info:
            return None
        
        duration = info['duration_seconds']
        
        # Calcular intervalos para extração de frames
        intervals = [i * duration / (num_frames + 1) for i in range(1, num_frames + 1)]
        
        frames = []
        for i, timestamp in enumerate(intervals):
            output_file = os.path.join(output_dir, f"frame_{i+1:03d}.jpg")
            
            # Comando para extrair frame
            cmd = [
                'ffmpeg',
                '-y',
                '-ss', str(timestamp),
                '-i', video_path,
                '-vframes', '1',
                '-q:v', '2',
                output_file
            ]
            
            # Executar comando
            subprocess.run(cmd, capture_output=True, check=True)
            
            frames.append(output_file)
            logger.info(f"Frame extraído: {output_file}")
        
        return frames
    
    except Exception as e:
        logger.error(f"Erro ao extrair frames do vídeo {video_path}: {e}")
        return None

def extrair_audio(video_path, output_dir):
    """
    Extrai o áudio do vídeo para análise.
    
    Args:
        video_path: Caminho para o arquivo de vídeo
        output_dir: Diretório de saída para o áudio
        
    Returns:
        str: Caminho para o arquivo de áudio extraído ou None em caso de erro
    """
    try:
        # Criar diretório de saída
        os.makedirs(output_dir, exist_ok=True)
        
        # Definir arquivo de saída
        output_file = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(video_path))[0]}.mp3")
        
        # Comando para extrair áudio
        cmd = [
            'ffmpeg',
            '-y',
            '-i', video_path,
            '-q:a', '0',
            '-map', 'a',
            output_file
        ]
        
        # Executar comando
        subprocess.run(cmd, capture_output=True, check=True)
        
        logger.info(f"Áudio extraído: {output_file}")
        
        return output_file
    
    except Exception as e:
        logger.error(f"Erro ao extrair áudio do vídeo {video_path}: {e}")
        return None

def analisar_video(video_path, output_dir):
    """
    Analisa um vídeo e extrai informações para machine learning.
    
    Args:
        video_path: Caminho para o arquivo de vídeo
        output_dir: Diretório de saída para os resultados
        
    Returns:
        dict: Informações da análise ou None em caso de erro
    """
    try:
        # Criar diretório de saída
        video_name = os.path.splitext(os.path.basename(video_path))[0]
        video_output_dir = os.path.join(output_dir, video_name)
        os.makedirs(video_output_dir, exist_ok=True)
        
        # Extrair informações básicas
        info = extrair_info_video(video_path)
        if not info:
            return None
        
        # Extrair frames
        frames_dir = os.path.join(video_output_dir, 'frames')
        frames = extrair_frames(video_path, frames_dir)
        
        # Extrair áudio
        audio_dir = os.path.join(video_output_dir, 'audio')
        audio = extrair_audio(video_path, audio_dir)
        
        # Adicionar informações à análise
        analysis = {
            'video_info': info,
            'frames': frames,
            'audio': audio,
            'analysis_timestamp': datetime.now().isoformat()
        }
        
        # Salvar análise em JSON
        analysis_file = os.path.join(video_output_dir, 'analysis.json')
        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2)
        
        logger.info(f"Análise concluída: {analysis_file}")
        
        return analysis
    
    except Exception as e:
        logger.error(f"Erro ao analisar vídeo {video_path}: {e}")
        return None

def analisar_videos(videos_dir, output_dir):
    """
    Analisa todos os vídeos em um diretório.
    
    Args:
        videos_dir: Diretório contendo os vídeos
        output_dir: Diretório de saída para os resultados
        
    Returns:
        dict: Resumo das análises
    """
    # Criar diretório de saída
    os.makedirs(output_dir, exist_ok=True)
    
    # Listar vídeos
    videos = [os.path.join(videos_dir, f) for f in os.listdir(videos_dir) 
              if f.lower().endswith(('.mp4', '.mov', '.avi', '.mkv'))]
    
    logger.info(f"Encontrados {len(videos)} vídeos para análise")
    
    # Analisar cada vídeo
    analyses = {}
    for video in videos:
        logger.info(f"Analisando vídeo: {video}")
        analysis = analisar_video(video, output_dir)
        if analysis:
            analyses[os.path.basename(video)] = analysis
    
    # Salvar resumo em JSON
    summary = {
        'total_videos': len(videos),
        'analyzed_videos': len(analyses),
        'videos': list(analyses.keys()),
        'analysis_timestamp': datetime.now().isoformat()
    }
    
    summary_file = os.path.join(output_dir, 'summary.json')
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
    
    logger.info(f"Análise de vídeos concluída: {summary_file}")
    
    return summary

def main():
    """
    Função principal.
    """
    # Configurar argumentos da linha de comando
    parser = argparse.ArgumentParser(description="Analisador de vídeos de referência")
    parser.add_argument("--videos", help="Diretório contendo os vídeos de referência", 
                        default="/Users/renatosantannasilva/Documents/augment-projects/CloneIA/reference/videos")
    parser.add_argument("--output", help="Diretório de saída para os resultados", 
                        default="analysis/videos")
    parser.add_argument("--debug", action="store_true", help="Ativar modo de depuração")

    args = parser.parse_args()

    # Configurar nível de log
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    # Analisar vídeos
    summary = analisar_videos(args.videos, args.output)
    
    if summary:
        logger.info(f"Análise concluída com sucesso: {summary['analyzed_videos']} vídeos analisados")
        return 0
    else:
        logger.error("Falha ao analisar vídeos")
        return 1

if __name__ == "__main__":
    sys.exit(main())
